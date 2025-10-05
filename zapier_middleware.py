"""
Google Gemini Alternative Middleware
===================================
Uses Google Gemini instead of OpenAI for AI analysis.
Much cheaper and better rate limits!
"""

from flask import Flask, request, jsonify
import requests
import os
import logging
import traceback
import time
import random
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
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # New: Google Gemini API key


@app.route('/')
def home():
    return jsonify({
        'status': 'active',
        'service': 'Zoho Desk Call Processor Middleware',
        'version': '2.2 - Google Gemini'
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
        
        # Analyze concern and mood using Gemini
        logger.info("Analyzing concern and mood with Gemini...")
        concern, mood = analyze_with_gemini(transcription, call_time, duration, direction)
        
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
            "diarize": "true"
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


def analyze_with_gemini(transcription, call_time, duration, direction):
    """
    Analyze call using Google Gemini API.
    Much cheaper and better rate limits than OpenAI!
    """
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        
        prompt = f"""Analyze this customer service call transcription and provide:

**Call Details:**
- Direction: {direction}
- Duration: {duration}
- Time: {call_time}

**Transcription:**
"{transcription}"

**Analysis Required:**
1. **Concern**: What is the specific reason for this call? What does the customer need or want?
2. **Mood**: What is the caller's emotional tone? (Professional, Polite, Frustrated, Confused, Anxious, etc.)

**Special Cases:**
- If only hold messages: "Caller on hold - No conversation recorded"
- If brief/dropped call: "Brief/Dropped call - Insufficient conversation"
- Otherwise: Analyze the actual conversation

**Response Format:**
Concern: [specific detailed concern]
Mood: [single word describing emotional tone]"""
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 150
            }
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # Parse concern and mood
            concern = "General inquiry"
            mood = "Neutral"
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('Concern:'):
                    concern = line.replace('Concern:', '').strip()
                elif line.startswith('Mood:'):
                    mood = line.replace('Mood:', '').strip()
            
            logger.info(f"Gemini Analysis: Concern='{concern}', Mood='{mood}'")
            return concern, mood
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return "Analysis unavailable", "Neutral"
            
    except Exception as e:
        logger.error(f"Error analyzing with Gemini: {e}")
        return "Analysis error", "Neutral"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
