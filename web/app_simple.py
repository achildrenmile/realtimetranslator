"""
Real-Time Voice Translator - Web Interface (Simplified for Local Testing)
Uses same translation backend as desktop app

Features:
- Web-based interface
- Text translation (works immediately)
- Simple deployment
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'achildrenmile-translator-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simple translator using MyMemory API (same as desktop app)
import urllib.request
import urllib.parse

class SimpleTranslator:
    """Simple translator using free MyMemory API"""
    
    @staticmethod
    def translate(text, source_lang, target_lang):
        """Translate text using MyMemory API"""
        if not text or not text.strip():
            return ""
            
        try:
            lang_pair = f"{source_lang}|{target_lang}"
            params = {
                "q": text,
                "langpair": lang_pair
            }
            
            url = f"https://api.mymemory.translated.net/get?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get('responseStatus') == 200:
                    return result.get('responseData', {}).get('translatedText', '')
                return "[Translation unavailable]"
        except Exception as e:
            return f"[Translation error: {str(e)}]"

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index_simple.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'translation': 'ready'
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', {'message': 'Connected to translator service'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('translate_text')
def handle_text_translation(data):
    """Handle text translation"""
    try:
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'zh')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            emit('translation_result', {'error': 'No text provided'})
            return
        
        translated = SimpleTranslator.translate(text, source_lang, target_lang)
        
        emit('translation_result', {
            'original': text,
            'translated': translated,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
    except Exception as e:
        emit('translation_result', {'error': str(e)})

@socketio.on('recognize_speech')
def handle_speech_recognition(data):
    """Handle speech recognition from audio using Google Speech API"""
    try:
        import speech_recognition as sr
        import base64
        import io
        import wave
        
        audio_base64 = data.get('audio', '')
        language = data.get('language', 'en')
        
        if not audio_base64:
            emit('recognition_result', {'error': 'No audio provided'})
            return
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64.split(',')[1] if ',' in audio_base64 else audio_base64)
        
        # Create AudioData object
        recognizer = sr.Recognizer()
        
        # Convert to AudioData format
        audio_data = sr.AudioData(audio_bytes, 16000, 2)
        
        # Recognize speech using Google
        lang_code = "zh-CN" if language == 'zh' else "en-US"
        try:
            recognized_text = recognizer.recognize_google(audio_data, language=lang_code)
            emit('recognition_result', {
                'text': recognized_text,
                'language': language
            })
        except sr.UnknownValueError:
            emit('recognition_result', {'error': 'Could not understand audio'})
        except sr.RequestError as e:
            emit('recognition_result', {'error': f'Recognition service error: {e}'})
            
    except ImportError:
        emit('recognition_result', {'error': 'SpeechRecognition not installed'})
    except Exception as e:
        emit('recognition_result', {'error': str(e)})

@socketio.on('translate_audio')
def handle_audio_translation(data):
    """Handle full audio -> recognition -> translation pipeline"""
    try:
        import speech_recognition as sr
        import base64
        import io
        
        audio_base64 = data.get('audio', '')
        source_lang = data.get('source_lang', 'zh')
        target_lang = data.get('target_lang', 'en')
        
        if not audio_base64:
            emit('full_translation_result', {'error': 'No audio provided'})
            return
        
        print(f"\nReceived audio data for translation")
        print(f"Source language: {source_lang}, Target: {target_lang}")
        
        # Decode base64 audio (should be WAV format from browser)
        try:
            audio_bytes = base64.b64decode(audio_base64.split(',')[1] if ',' in audio_base64 else audio_base64)
            print(f"Decoded {len(audio_bytes)} bytes of audio data")
        except Exception as e:
            print(f"Base64 decode error: {e}")
            emit('full_translation_result', {'error': 'Invalid audio data encoding'})
            return
        
        # Create recognizer and process WAV audio
        recognizer = sr.Recognizer()
        
        # Adjust recognizer settings for better accuracy
        recognizer.energy_threshold = 300  # Lower threshold for quieter environments
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8  # Shorter pause detection
        
        try:
            # Create AudioFile from WAV bytes
            wav_io = io.BytesIO(audio_bytes)
            with sr.AudioFile(wav_io) as source:
                # Adjust for ambient noise
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                # Record the audio
                audio_data = recognizer.record(source)
                print(f"Audio loaded successfully, duration: ~{len(audio_data.frame_data) / (audio_data.sample_rate * audio_data.sample_width):.2f}s")
        except Exception as e:
            print(f"Error loading audio file: {e}")
            emit('full_translation_result', {
                'error': f'Failed to process audio file. Please ensure microphone is working properly.'
            })
            return
        
        # Recognize speech using Google Speech Recognition
        lang_code = "zh-CN" if source_lang == 'zh' else "en-US"
        print(f"Attempting speech recognition with language: {lang_code}")
        print(f"Energy threshold: {recognizer.energy_threshold}")
        
        try:
            # Try with show_all to see what alternatives Google found
            recognized_text = recognizer.recognize_google(audio_data, language=lang_code, show_all=False)
            print(f"✓ Speech recognized: '{recognized_text}'")
        except sr.UnknownValueError:
            print("✗ Speech recognition failed - audio not understood")
            print("   Possible reasons: background noise, unclear speech, wrong language selected")
            print(f"   Try: 1) Speak louder/clearer, 2) Reduce background noise, 3) Check language selection ({lang_code})")
            emit('full_translation_result', {
                'error': f'Could not understand the audio.\n\nTips:\n• Speak clearly and closer to microphone\n• Reduce background noise\n• Verify language selection (currently: {lang_code})\n• Try speaking louder'
            })
            return
        except sr.RequestError as e:
            print(f"✗ Google Speech API error: {e}")
            emit('full_translation_result', {
                'error': f'Speech recognition service error: {e}. Please check your internet connection.'
            })
            return
        
        # Translate the recognized text
        print(f"Translating from {source_lang} to {target_lang}...")
        translated_text = SimpleTranslator.translate(recognized_text, source_lang, target_lang)
        print(f"✓ Translation complete: '{translated_text}'")
        
        # Send result back to client
        emit('full_translation_result', {
            'original': recognized_text,
            'translated': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
        
    except Exception as e:
        print(f"\n✗ Unexpected error in audio translation:")
        import traceback
        traceback.print_exc()
        emit('full_translation_result', {
            'error': f'Server error: {str(e)}. Check server console for details.'
        })

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8080))
    print(f"\n{'='*50}")
    print(f"  Voice Translator Web App Starting")
    print(f"{'='*50}")
    print(f"\n  URL: http://localhost:{port}")
    print(f"\n  Press Ctrl+C to stop\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
