#!/usr/bin/env python3
"""
Zoho Desk Call Ticket Processor
- Fetches calls from Exotel
- Transcribes using Deepgram
- Analyzes concern and mood
- Creates Zoho Desk tickets with transcription notes
"""

import asyncio
import aiohttp
import sys
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zoho_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ZohoDeskIntegration:
    """Handle creating tickets in Zoho Desk for call records."""
    
    def __init__(self):
        self.enabled = os.getenv('ZOHO_DESK_ENABLED', 'false').lower() == 'true'
        self.org_id = os.getenv('ZOHO_DESK_ORG_ID')
        self.access_token = os.getenv('ZOHO_DESK_ACCESS_TOKEN')
        self.refresh_token = os.getenv('ZOHO_DESK_REFRESH_TOKEN')
        self.client_id = os.getenv('ZOHO_DESK_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_DESK_CLIENT_SECRET')
        self.department_id = os.getenv('ZOHO_DESK_DEPARTMENT_ID')
        self.api_domain = os.getenv('ZOHO_DESK_API_DOMAIN', 'https://desk.zoho.com')
        self.default_priority = os.getenv('ZOHO_DESK_DEFAULT_PRIORITY', 'Medium')
        self.auto_create_contact = os.getenv('ZOHO_DESK_AUTO_CREATE_CONTACT', 'true').lower() == 'true'
        
        if self.enabled and not all([self.org_id, self.access_token, self.department_id]):
            logger.warning("Zoho Desk is enabled but missing required credentials")
            self.enabled = False
            
    async def refresh_access_token(self):
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
            
        try:
            url = "https://accounts.zoho.com/oauth/v2/token"
            params = {
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.access_token = data.get("access_token")
                        logger.info("Successfully refreshed Zoho access token")
                        
                        # Update .env file with new token
                        self._update_env_token(self.access_token)
                        return True
                    else:
                        logger.error(f"Failed to refresh token: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False
    
    def _update_env_token(self, new_token):
        """Update access token in .env file."""
        try:
            env_path = Path(".env")
            if env_path.exists():
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                with open(env_path, 'w') as f:
                    for line in lines:
                        if line.startswith('ZOHO_DESK_ACCESS_TOKEN='):
                            f.write(f'ZOHO_DESK_ACCESS_TOKEN={new_token}\n')
                        else:
                            f.write(line)
        except Exception as e:
            logger.error(f"Error updating .env file: {e}")
    
    def get_headers(self):
        """Get API headers with authentication."""
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "orgId": self.org_id,
            "Content-Type": "application/json"
        }
    
    async def find_or_create_contact(self, phone_number, session):
        """Find existing contact by phone or create new one."""
        try:
            # Search for existing contact
            search_url = f"{self.api_domain}/api/v1/contacts/search"
            params = {"phone": phone_number}
            
            async with session.get(search_url, headers=self.get_headers(), params=params) as resp:
                if resp.status == 401:
                    # Token expired, try refresh
                    logger.info("Token expired, refreshing...")
                    if await self.refresh_access_token():
                        # Retry with new token
                        async with session.get(search_url, headers=self.get_headers(), params=params) as retry_resp:
                            if retry_resp.status == 200:
                                data = await retry_resp.json()
                                contacts = data.get("data", [])
                                if contacts:
                                    contact_id = contacts[0].get("id")
                                    logger.info(f"Found existing Zoho contact: {contact_id} for {phone_number}")
                                    return contact_id
                elif resp.status == 200:
                    data = await resp.json()
                    contacts = data.get("data", [])
                    if contacts:
                        contact_id = contacts[0].get("id")
                        logger.info(f"Found existing Zoho contact: {contact_id} for {phone_number}")
                        return contact_id
            
            # Create new contact if not found
            if self.auto_create_contact:
                create_url = f"{self.api_domain}/api/v1/contacts"
                contact_data = {
                    "lastName": f"Customer {phone_number[-4:]}",
                    "phone": phone_number,
                    "description": f"Auto-created from Exotel call"
                }
                
                async with session.post(create_url, headers=self.get_headers(), json=contact_data) as resp:
                    if resp.status in [200, 201]:
                        data = await resp.json()
                        contact_id = data.get("id")
                        logger.info(f"Created new Zoho contact: {contact_id} for {phone_number}")
                        return contact_id
                    else:
                        logger.error(f"Failed to create Zoho contact: {resp.status} - {await resp.text()}")
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding/creating Zoho contact: {e}")
            return None
    
    async def create_ticket(self, call_data):
        """Create a support ticket in Zoho Desk for a call with transcription in notes."""
        if not self.enabled:
            logger.info("Zoho Desk integration not enabled, skipping")
            return False
        
        try:
            # Extract call information
            customer_number = call_data.get("customer_number", "Unknown")
            agent_name = call_data.get("agent_name", "Unknown")
            duration = call_data.get("duration", "Unknown")
            call_time = call_data.get("formatted_date", "Unknown")
            transcription = call_data.get("transcript", "No transcription available")
            concern = call_data.get("concern", "Call inquiry")
            mood = call_data.get("mood", "Neutral")
            call_sid = call_data.get("call_id", "Unknown")
            recording_url = call_data.get("recording_url", "")
            call_direction = call_data.get("call_direction", "Unknown")
            
            # Prepare clean ticket description (without transcription)
            description = f"""Call from {customer_number}

📞 Call Details:
• Agent: {agent_name}
• Time: {call_time}
• Duration: {duration}
• Direction: {call_direction}
• Mood: {mood}

🎯 Concern Identified:
{concern}

🎧 Recording: {recording_url if recording_url else 'Not available'}

Call ID: {call_sid}
---
Auto-generated from Exotel call processing system"""
            
            async with aiohttp.ClientSession() as session:
                # Find or create contact
                contact_id = None
                if self.auto_create_contact:
                    contact_id = await self.find_or_create_contact(customer_number, session)
                
                # Step 1: Create ticket
                ticket_url = f"{self.api_domain}/api/v1/tickets"
                
                ticket_data = {
                    "subject": f"Call from {customer_number} - {concern[:50]}",
                    "departmentId": self.department_id,
                    "description": description,
                    "priority": self.default_priority,
                    "channel": "Phone",
                    "status": "Open"
                }
                
                # Add contact if found/created
                if contact_id:
                    ticket_data["contactId"] = contact_id
                
                async with session.post(ticket_url, headers=self.get_headers(), json=ticket_data) as resp:
                    if resp.status == 401:
                        # Token expired, refresh and retry
                        logger.info("Token expired during ticket creation, refreshing...")
                        if await self.refresh_access_token():
                            async with session.post(ticket_url, headers=self.get_headers(), json=ticket_data) as retry_resp:
                                if retry_resp.status in [200, 201]:
                                    data = await retry_resp.json()
                                    ticket_id = data.get("id")
                                    ticket_number = data.get("ticketNumber", "Unknown")
                                    logger.info(f"✓ Created Zoho Desk ticket #{ticket_number} (ID: {ticket_id}) for call {call_sid}")
                                    
                                    # Step 2: Add transcription as a private note
                                    if ticket_id and transcription:
                                        note_added = await self.add_transcription_note(ticket_id, transcription, call_sid, session)
                                        if note_added:
                                            logger.info(f"✓ Added transcription note to ticket #{ticket_number}")
                                        else:
                                            logger.warning(f"⚠ Ticket created but failed to add transcription note")
                                    
                                    return True
                                else:
                                    error_text = await retry_resp.text()
                                    logger.error(f"Failed to create Zoho ticket after refresh: {retry_resp.status} - {error_text}")
                                    return False
                    elif resp.status in [200, 201]:
                        data = await resp.json()
                        ticket_id = data.get("id")
                        ticket_number = data.get("ticketNumber", "Unknown")
                        logger.info(f"✓ Created Zoho Desk ticket #{ticket_number} (ID: {ticket_id}) for call {call_sid}")
                        
                        # Step 2: Add transcription as a private note
                        if ticket_id and transcription:
                            note_added = await self.add_transcription_note(ticket_id, transcription, call_sid, session)
                            if note_added:
                                logger.info(f"✓ Added transcription note to ticket #{ticket_number}")
                            else:
                                logger.warning(f"⚠ Ticket created but failed to add transcription note")
                        
                        return True
                    else:
                        error_text = await resp.text()
                        logger.error(f"Failed to create Zoho ticket: {resp.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error creating Zoho Desk ticket: {e}")
            return False
    
    async def add_transcription_note(self, ticket_id, transcription, call_sid, session):
        """Add transcription as a note to an existing ticket."""
        try:
            note_url = f"{self.api_domain}/api/v1/tickets/{ticket_id}/comments"
            
            note_content = f"""📝 **Call Transcription**

{transcription}

---
Call ID: {call_sid}
*Auto-generated transcription from Exotel recording*"""
            
            note_data = {
                "content": note_content,
                "isPublic": False,  # Make it a private note (internal only)
                "contentType": "plainText"
            }
            
            async with session.post(note_url, headers=self.get_headers(), json=note_data) as resp:
                if resp.status == 401:
                    # Token expired, refresh and retry
                    if await self.refresh_access_token():
                        async with session.post(note_url, headers=self.get_headers(), json=note_data) as retry_resp:
                            return retry_resp.status in [200, 201]
                return resp.status in [200, 201]
                    
        except Exception as e:
            logger.error(f"Error adding transcription note: {e}")
            return False


class AgentManager:
    def __init__(self, config_file='agents_config.json'):
        self.config_file = config_file
        self.agents = {}
        self.default_agent = {}
        self.load_config()
    
    def load_config(self):
        """Load agent configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.agents = config.get('agents', {})
                    self.default_agent = config.get('default_agent', {})
                logger.info(f"Loaded {len(self.agents)} agents from config")
            else:
                logger.warning(f"Config file {self.config_file} not found, using defaults")
                self.create_default_config()
        except Exception as e:
            logger.error(f"Error loading agent config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default agent configuration."""
        self.agents = {
            "09631084471": {
                "name": "Prateek",
                "department": "Customer Success",
                "active": True
            }
        }
        self.default_agent = self.agents["09631084471"]


class ZohoCallProcessor:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.zoho_desk = ZohoDeskIntegration()
        self.processed_calls = set()
        self.load_processed_calls()
        
        # Get credentials from environment
        self.exotel_sid = os.getenv('EXOTEL_SID')
        self.exotel_api_key = os.getenv('EXOTEL_API_KEY')
        self.exotel_api_token = os.getenv('EXOTEL_API_TOKEN')
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
    def load_processed_calls(self):
        """Load previously processed calls to avoid duplicates."""
        try:
            if os.path.exists('processed_calls.json'):
                with open('processed_calls.json', 'r') as f:
                    self.processed_calls = set(json.load(f))
                logger.info(f"Loaded {len(self.processed_calls)} previously processed calls")
        except Exception as e:
            logger.error(f"Error loading processed calls: {e}")
            self.processed_calls = set()
    
    def save_processed_calls(self):
        """Save processed calls list."""
        try:
            with open('processed_calls.json', 'w') as f:
                json.dump(list(self.processed_calls), f)
        except Exception as e:
            logger.error(f"Error saving processed calls: {e}")
    
    async def fetch_latest_calls(self):
        """Fetch latest calls from Exotel API."""
        if not all([self.exotel_api_key, self.exotel_api_token, self.exotel_sid]):
            logger.error("Exotel API credentials not configured")
            return []
        
        url = f"https://api.exotel.com/v1/Accounts/{self.exotel_sid}/Calls.json"
        
        try:
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.exotel_api_key, self.exotel_api_token)
                params = {'PageSize': 10, 'Page': 0}
                async with session.get(url, auth=auth, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        calls = data.get('Calls', [])
                        
                        # Filter for completed calls with recordings
                        completed_calls = []
                        for call in calls:
                            if (call.get('Status') == 'completed' and 
                                call.get('RecordingUrl') and
                                call.get('Sid') not in self.processed_calls):
                                completed_calls.append(call)
                        
                        logger.info(f"Found {len(completed_calls)} new calls to process")
                        return completed_calls
                    else:
                        logger.error(f"Failed to fetch calls: {resp.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching calls: {e}")
            return []
    
    async def download_recording(self, call_id, recording_url):
        """Download call recording from Exotel."""
        try:
            filename = f"recordings/{call_id}.mp3"
            os.makedirs("recordings", exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.exotel_api_key, self.exotel_api_token)
                async with session.get(recording_url, auth=auth) as resp:
                    if resp.status == 200:
                        with open(filename, 'wb') as f:
                            f.write(await resp.read())
                        logger.info(f"Downloaded recording: {filename}")
                        return filename
                    else:
                        logger.error(f"Failed to download recording: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading recording: {e}")
            return None
    
    async def transcribe_audio(self, audio_file):
        """Transcribe audio using Deepgram."""
        if not self.deepgram_api_key:
            logger.error("Deepgram API key not configured")
            return None
        
        try:
            url = "https://api.deepgram.com/v1/listen"
            
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "audio/mpeg"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=audio_data) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        transcript = data.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
                        logger.info(f"Transcription completed: {len(transcript)} characters")
                        return transcript
                    else:
                        logger.error(f"Transcription failed: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def analyze_concern_and_mood(self, transcript):
        """Analyze concern and mood from transcript using OpenAI."""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured, using keyword analysis")
            return self._analyze_with_keywords(transcript)
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI assistant analyzing customer service calls. Provide a brief concern summary (1-2 sentences) and mood (Positive/Neutral/Negative/Urgent)."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this call transcript and provide:\n1. Main concern (brief)\n2. Customer mood\n\nTranscript: {transcript[:1000]}"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 150
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data['choices'][0]['message']['content']
                        
                        # Parse response
                        lines = response.split('\n')
                        concern = "Call inquiry"
                        mood = "Neutral"
                        
                        for line in lines:
                            if 'concern' in line.lower() or '1.' in line:
                                concern = line.split(':', 1)[-1].strip()
                            elif 'mood' in line.lower() or '2.' in line:
                                mood = line.split(':', 1)[-1].strip()
                        
                        return concern, mood
                    else:
                        logger.warning(f"OpenAI API error: {resp.status}, using keyword analysis")
                        return self._analyze_with_keywords(transcript)
                        
        except Exception as e:
            logger.warning(f"Error with OpenAI analysis: {e}, using keyword analysis")
            return self._analyze_with_keywords(transcript)
    
    def _analyze_with_keywords(self, transcript):
        """Fallback keyword-based analysis."""
        transcript_lower = transcript.lower()
        
        # Mood analysis
        if any(word in transcript_lower for word in ['urgent', 'emergency', 'immediately', 'asap']):
            mood = "Urgent"
        elif any(word in transcript_lower for word in ['angry', 'frustrated', 'disappointed', 'upset']):
            mood = "Negative"
        elif any(word in transcript_lower for word in ['thank', 'great', 'happy', 'satisfied', 'excellent']):
            mood = "Positive"
        else:
            mood = "Neutral"
        
        # Concern analysis
        if any(word in transcript_lower for word in ['billing', 'payment', 'charge', 'invoice']):
            concern = "Billing inquiry"
        elif any(word in transcript_lower for word in ['technical', 'not working', 'error', 'problem', 'issue']):
            concern = "Technical support request"
        elif any(word in transcript_lower for word in ['refund', 'return', 'cancel']):
            concern = "Refund/cancellation request"
        elif any(word in transcript_lower for word in ['question', 'how to', 'help with']):
            concern = "General inquiry - assistance needed"
        else:
            concern = f"Call regarding: {transcript[:100]}..."
        
        return concern, mood
    
    async def process_call(self, call):
        """Process a single call."""
        call_id = call.get('Sid')
        logger.info(f"Processing call: {call_id}")
        
        try:
            # Get call details
            caller_number = call.get('From', {}).get('PhoneNumber', 'Unknown')
            called_number = call.get('To', {}).get('PhoneNumber', 'Unknown')
            duration_seconds = int(call.get('Duration', 0))
            duration = f"{duration_seconds // 60}m {duration_seconds % 60}s"
            call_time = call.get('DateCreated', 'Unknown')
            recording_url = call.get('RecordingUrl')
            
            # Detect agent
            agent_number = None
            customer_number = None
            
            for number in self.agent_manager.agents.keys():
                if number in caller_number or number in called_number:
                    agent_number = number
                    if number in caller_number:
                        customer_number = called_number
                        direction = "Outgoing call to Customer"
                    else:
                        customer_number = caller_number
                        direction = "Incoming call from Customer"
                    break
            
            if not agent_number:
                logger.warning(f"No agent detected for call {call_id}, skipping")
                return False
            
            agent_info = self.agent_manager.agents[agent_number]
            
            # Step 1: Download recording
            file_path = await self.download_recording(call_id, recording_url)
            if not file_path:
                logger.error(f"Failed to download recording for {call_id}")
                return False
            
            # Step 2: Transcribe
            transcript = await self.transcribe_audio(file_path)
            if not transcript:
                logger.error(f"Failed to transcribe {call_id}")
                return False
            
            # Step 3: Analyze concern and mood
            concern, mood = await self.analyze_concern_and_mood(transcript)
            
            # Step 4: Create Zoho Desk ticket
            ticket_data = {
                "call_id": call_id,
                "customer_number": customer_number,
                "agent_number": agent_number,
                "agent_name": agent_info['name'],
                "agent_department": agent_info.get('department', 'Customer Success'),
                "duration": duration,
                "formatted_date": call_time,
                "recording_url": recording_url,
                "call_direction": direction,
                "concern": concern,
                "mood": mood,
                "transcript": transcript
            }
            
            success = await self.zoho_desk.create_ticket(ticket_data)
            
            if success:
                self.processed_calls.add(call_id)
                self.save_processed_calls()
                logger.info(f"Successfully processed call {call_id}")
                return True
            else:
                logger.error(f"Failed to create ticket for {call_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing call {call_id}: {e}")
            return False
    
    async def run_monitoring_cycle(self):
        """Run one monitoring cycle."""
        logger.info("Starting monitoring cycle...")
        
        # Fetch new calls
        calls = await self.fetch_latest_calls()
        
        if not calls:
            logger.info("No new calls to process")
            return
        
        # Process each call
        processed_count = 0
        for call in calls:
            success = await self.process_call(call)
            if success:
                processed_count += 1
        
        logger.info(f"Monitoring cycle complete: {processed_count}/{len(calls)} calls processed")
    
    async def run_continuous(self, interval_minutes=1):
        """Run continuous monitoring."""
        logger.info(f"Starting continuous monitoring (checking every {interval_minutes} minute(s))")
        logger.info(f"Configured agents: {list(self.agent_manager.agents.keys())}")
        
        while True:
            try:
                await self.run_monitoring_cycle()
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
            
            # Wait before next cycle
            await asyncio.sleep(interval_minutes * 60)


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Zoho Desk Call Ticket Processor Starting...")
    logger.info("=" * 60)
    
    processor = ZohoCallProcessor()
    
    try:
        asyncio.run(processor.run_continuous(interval_minutes=1))
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    main()

