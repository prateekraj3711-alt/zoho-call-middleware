#!/usr/bin/env python3
"""
Lightweight Zapier Middleware for Zoho Desk Tickets
Handles: Exotel call fetching, transcription, and returns data to Zapier
"""

from flask import Flask, request, jsonify
import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
EXOTEL_SID = os.getenv('EXOTEL_SID')
EXOTEL_API_KEY = os.getenv('EXOTEL_API_KEY')
EXOTEL_API_TOKEN = os.getenv('EXOTEL_API_TOKEN')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Simple in-memory tracking of processed calls
processed_calls = set()


def fetch_latest_call():
    """Fetch the latest unprocessed call from Exotel."""
    try:
        url = f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls.json"
        auth = (EXOTEL_API_KEY, EXOTEL_API_TOKEN)
        params = {'PageSize': 10, 'Page': 0}
        
        response = requests.get(url, auth=auth, params=params, timeout=10)
        
        if response.status_code == 200:
            calls = response.json().get('Calls', [])
            
            # Find first completed call with recording that hasn't been processed
            for call in calls:
                call_id = call.get('Sid')
                if (call.get('Status') == 'completed' and 
                    call.get('RecordingUrl') and 
                    call_id not in processed_calls):
                    return call
            
            return None
        else:
            logger.error(f"Failed to fetch calls: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return None


def download_recording(recording_url):
    """Download recording from Exotel."""
    try:
        auth = (EXOTEL_API_KEY, EXOTEL_API_TOKEN)
        response = requests.get(recording_url, auth=auth, timeout=30)
        
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Failed to download recording: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error downloading recording: {e}")
        return None


def transcribe_audio(audio_data):
    """Transcribe audio using Deepgram."""
    if not DEEPGRAM_API_KEY:
        return None
    
    try:
        url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/mpeg"
        }
        
        response = requests.post(url, headers=headers, data=audio_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            transcript = data.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
            logger.info(f"Transcription completed: {len(transcript)} characters")
            return transcript
        else:
            logger.error(f"Transcription failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error transcribing: {e}")
        return None


def analyze_concern_and_mood(transcript):
    """Analyze concern and mood using OpenAI or keywords."""
    if not transcript:
        return "Call inquiry", "Neutral"
    
    # Try OpenAI first
    if OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
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
                        "content": f"Analyze this call transcript:\n\n{transcript[:1000]}\n\nProvide:\n1. Main concern (brief)\n2. Customer mood"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 150
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data['choices'][0]['message']['content']
                
                # Parse response
                lines = response_text.split('\n')
                concern = "Call inquiry"
                mood = "Neutral"
                
                for line in lines:
                    if 'concern' in line.lower() or '1.' in line:
                        concern = line.split(':', 1)[-1].strip()
                    elif 'mood' in line.lower() or '2.' in line:
                        mood = line.split(':', 1)[-1].strip()
                
                return concern, mood
                
        except Exception as e:
            logger.warning(f"OpenAI analysis failed: {e}, using keyword analysis")
    
    # Fallback to keyword analysis
    return analyze_with_keywords(transcript)


def analyze_with_keywords(transcript):
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
        concern = "General inquiry"
    else:
        concern = f"Call regarding: {transcript[:80]}..." if len(transcript) > 80 else "Call inquiry"
    
    return concern, mood


@app.route('/', methods=['GET'])
def home():
    """Health check endpoint."""
    return jsonify({
        "status": "running",
        "service": "Zoho Desk Call Middleware",
        "endpoints": {
            "/": "Health check",
            "/process_call": "Process latest Exotel call (POST)",
            "/health": "Detailed health check"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Detailed health check."""
    return jsonify({
        "status": "healthy",
        "exotel_configured": bool(EXOTEL_SID and EXOTEL_API_KEY),
        "deepgram_configured": bool(DEEPGRAM_API_KEY),
        "openai_configured": bool(OPENAI_API_KEY),
        "processed_calls_count": len(processed_calls)
    })


@app.route('/process_call', methods=['POST'])
def process_call():
    """
    Main endpoint for Zapier to call.
    Fetches latest call, downloads recording, transcribes, analyzes, and returns data.
    """
    try:
        logger.info("Processing call request from Zapier...")
        
        # Step 1: Fetch latest call
        call = fetch_latest_call()
        
        if not call:
            return jsonify({
                "status": "no_new_calls",
                "message": "No new calls to process"
            }), 200
        
        call_id = call.get('Sid')
        logger.info(f"Processing call: {call_id}")
        
        # Extract call details
        from_number = call.get('From', {}).get('PhoneNumber', 'Unknown')
        to_number = call.get('To', {}).get('PhoneNumber', 'Unknown')
        duration_sec = int(call.get('Duration', 0))
        duration = f"{duration_sec // 60}m {duration_sec % 60}s"
        call_time = call.get('DateCreated', 'Unknown')
        recording_url = call.get('RecordingUrl', '')
        
        # Detect agent (customize based on your agent numbers)
        agent_numbers = ['09631084471']  # Add your agent numbers here
        
        agent_number = None
        customer_number = None
        direction = "Unknown"
        
        for agent in agent_numbers:
            if agent in from_number:
                agent_number = agent
                customer_number = to_number
                direction = "Outgoing"
                break
            elif agent in to_number:
                agent_number = agent
                customer_number = from_number
                direction = "Incoming"
                break
        
        if not agent_number:
            # Default to from/to logic
            customer_number = from_number
            agent_number = to_number
            direction = "Incoming"
        
        # Step 2: Download recording
        logger.info("Downloading recording...")
        audio_data = download_recording(recording_url)
        
        if not audio_data:
            processed_calls.add(call_id)
            return jsonify({
                "status": "error",
                "message": "Failed to download recording",
                "call_id": call_id
            }), 500
        
        # Step 3: Transcribe
        logger.info("Transcribing audio...")
        transcript = transcribe_audio(audio_data)
        
        if not transcript:
            transcript = f"Transcription unavailable. Call duration: {duration}"
        
        # Step 4: Analyze
        logger.info("Analyzing concern and mood...")
        concern, mood = analyze_concern_and_mood(transcript)
        
        # Step 5: Mark as processed
        processed_calls.add(call_id)
        
        # Return data to Zapier
        result = {
            "status": "success",
            "call_id": call_id,
            "customer_number": customer_number,
            "agent_number": agent_number,
            "duration": duration,
            "call_time": call_time,
            "call_direction": direction,
            "concern": concern,
            "mood": mood,
            "transcript": transcript,
            "transcription_length": len(transcript)
        }
        
        logger.info(f"Successfully processed call {call_id}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing call: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    # For local testing
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

