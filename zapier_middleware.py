"""
Improved Zapier Middleware with Better AI Analysis
==================================================
Deploy this to Render to replace the current middleware
"""

from flask import Flask, request, jsonify
import requests
import os
import logging
import traceback
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# API Credentials
EXOTEL_API_KEY = os.getenv('EXOTEL_API_KEY')
EXOTEL_API_TOKEN = os.getenv('EXOTEL_API_TOKEN')
EXOTEL_SID = os.getenv('EXOTEL_SID')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


@app.route('/')
def home():
    return jsonify({
        'status': 'active',
        'service': 'Zoho Desk Call Processor Middleware',
        'version': '2.0 - Improved Analysis'
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Service is running'}), 200


@app.route('/process_call', methods=['POST'])
def process_call():
    """Process the latest call from Exotel."""
    try:
        # Log incoming request
        incoming_data = request.get_json(force=True, silent=True) or {}
        logger.info(f"Received data from Zapier: {incoming_data}")
        logger.info("Processing call request from Zapier...")
        
        # Fetch latest call from Exotel
        call = fetch_latest_call()
        if not call:
            logger.info("No new calls to process")
            return jsonify({
                'status': 'no_new_calls',
                'call_id': '',
                'customer_number': '',
                'agent_number': '',
                'call_time': '',
                'duration': '',
                'call_direction': '',
                'transcript': '',
                'transcription_length': 0,
                'concern': '',
                'mood': '',
                'message': 'No new calls found'
            })
        
        call_sid = call.get('Sid')
        logger.info(f"Processing call: {call_sid}")
        
        # Extract call details
        from_number = str(call.get('From', 'Unknown'))
        to_number = str(call.get('To', 'Unknown'))
        call_time = call.get('StartTime', 'Unknown')
        duration_raw = call.get('Duration', 0)
        recording_url = call.get('RecordingUrl')
        direction = call.get('Direction', 'Unknown')
        
        # Convert duration to readable format
        try:
            duration_seconds = int(duration_raw)
            duration = f"{duration_seconds // 60}m {duration_seconds % 60}s"
        except:
            duration = "0m 0s"
        
        # Download recording
        logger.info("Downloading recording...")
        audio_content = download_recording(recording_url, call_sid)
        if not audio_content:
            logger.error("Failed to download recording")
            return jsonify({'status': 'error', 'message': 'Failed to download recording'}), 500
        
        # Transcribe
        logger.info("Transcribing audio...")
        transcription = transcribe_audio(audio_content)
        if not transcription:
            logger.error("Transcription failed")
            return jsonify({'status': 'error', 'message': 'Transcription failed'}), 500
        
        logger.info(f"Transcription completed: {len(transcription)} characters")
        
        # Analyze concern and mood with improved prompt
        logger.info("Analyzing concern and mood...")
        concern, mood = analyze_call_improved(transcription, call_time, duration, direction)
        
        # Prepare response
        response_data = {
            'status': 'success',
            'call_id': call_sid,
            'customer_number': from_number,
            'agent_number': to_number,
            'call_time': call_time,
            'duration': duration,
            'call_direction': direction,
            'transcript': transcription,
            'transcription_length': len(transcription),
            'concern': concern,
            'mood': mood
        }
        
        logger.info(f"Successfully processed call {call_sid}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Error processing call: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'call_id': '',
            'customer_number': '',
            'agent_number': '',
            'call_time': '',
            'duration': '',
            'call_direction': '',
            'transcript': '',
            'transcription_length': 0,
            'concern': '',
            'mood': ''
        }), 500


def fetch_latest_call():
    """Fetch the most recent completed call with recording from Exotel."""
    try:
        url = f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls.json"
        auth = requests.auth.HTTPBasicAuth(EXOTEL_API_KEY, EXOTEL_API_TOKEN)
        params = {'PageSize': 10, 'Page': 0}
        
        response = requests.get(url, auth=auth, params=params, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Exotel API error: {response.status_code}")
            return None
        
        data = response.json()
        calls = data.get('Calls', [])
        
        # Find the most recent completed call with a recording
        for call in calls:
            if call.get('Status') == 'completed' and call.get('RecordingUrl'):
                return call
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return None


def download_recording(recording_url, call_sid):
    """Download audio recording from Exotel."""
    try:
        auth = requests.auth.HTTPBasicAuth(EXOTEL_API_KEY, EXOTEL_API_TOKEN)
        response = requests.get(recording_url, auth=auth, timeout=60)
        
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Failed to download recording: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading recording: {e}")
        return None


def transcribe_audio(audio_content):
    """Transcribe audio using Deepgram."""
    try:
        url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"
        }
        params = {
            "model": "general",
            "language": "en",
            "punctuate": "true",
            "diarize": "true"  # Speaker identification
        }
        
        response = requests.post(url, headers=headers, params=params, data=audio_content, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            transcript = data.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
            return transcript
        else:
            logger.error(f"Deepgram API error: {response.status_code}")
            return ""
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""


def analyze_call_improved(transcription, call_time, duration, direction):
    """
    Improved analysis with better prompts to extract meaningful insights.
    """
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt for better analysis
        prompt = f"""You are analyzing a customer service call recording. Based on the transcription below, provide a detailed analysis.

**Call Information:**
- Direction: {direction}
- Duration: {duration}
- Time: {call_time}

**Transcription:**
"{transcription}"

**Your Task:**
1. **Concern**: Identify the SPECIFIC reason for the call. What exactly is the customer asking about, requesting, or trying to resolve? Be detailed and specific based on what was actually discussed. Examples:
   - "Requesting background verification documents"
   - "Follow-up on pending employment check status"
   - "Inquiry about account activation process"
   - "Technical support for login issues"
   - "Billing dispute regarding recent charges"
   
2. **Mood**: Assess the caller's emotional tone in ONE word from this list:
   - Professional, Polite, Cooperative, Satisfied, Neutral
   - Confused, Uncertain, Anxious, Concerned
   - Frustrated, Irritated, Angry, Urgent

**Important Notes:**
- If the transcription shows only hold music, IVR messages, or "call on hold" messages WITHOUT actual conversation, respond with:
  Concern: Caller on hold - No conversation recorded
  Mood: Unknown
  
- If it's a very short call (under 10 seconds) or dropped call, respond with:
  Concern: Brief/Dropped call - Insufficient conversation
  Mood: Unknown

- Otherwise, analyze the ACTUAL conversation content carefully.

**Response Format:**
Concern: [Your detailed, specific analysis of what the caller needs/wants]
Mood: [Single word from the list above]"""
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert customer service analyst. Provide accurate, specific insights based on call transcriptions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 150,
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            # Parse concern and mood
            concern = "General inquiry"
            mood = "Neutral"
            
            for line in analysis.split('\n'):
                line = line.strip()
                if line.startswith('Concern:'):
                    concern = line.replace('Concern:', '').strip()
                elif line.startswith('Mood:'):
                    mood = line.replace('Mood:', '').strip()
            
            logger.info(f"Analysis: Concern='{concern}', Mood='{mood}'")
            return concern, mood
        else:
            logger.error(f"OpenAI API error: {response.status_code}")
            return "Analysis unavailable", "Neutral"
            
    except Exception as e:
        logger.error(f"Error analyzing call: {e}")
        return "Analysis error", "Neutral"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

