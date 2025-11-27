"""
Real-Time Voice Translator - Web Interface
Fully offline, containerized version for OpenShift deployment

Features:
- Web-based interface (no desktop required)
- 100% offline operation (no internet needed)
- Runs entirely within container
- Offline speech recognition (Vosk)
- Offline translation (Argos Translate)
- WebSocket for real-time communication
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import argostranslate.package
import argostranslate.translate
import base64
import json
import io
import wave
import os
from vosk import Model, KaldiRecognizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'achildrenmile-translator-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for models
vosk_model_en = None
vosk_model_zh = None
translation_ready = False

def initialize_models():
    """Initialize all offline models on startup"""
    global vosk_model_en, vosk_model_zh, translation_ready
    
    print("Initializing models...")
    
    # Initialize Vosk models (offline speech recognition)
    model_path_en = os.getenv('VOSK_MODEL_EN', '/app/models/vosk-model-small-en-us-0.15')
    model_path_zh = os.getenv('VOSK_MODEL_ZH', '/app/models/vosk-model-small-cn-0.22')
    
    if os.path.exists(model_path_en):
        vosk_model_en = Model(model_path_en)
        print(f"✓ Loaded English model: {model_path_en}")
    else:
        print(f"⚠ English model not found: {model_path_en}")
    
    if os.path.exists(model_path_zh):
        vosk_model_zh = Model(model_path_zh)
        print(f"✓ Loaded Chinese model: {model_path_zh}")
    else:
        print(f"⚠ Chinese model not found: {model_path_zh}")
    
    # Initialize Argos Translate (offline translation)
    try:
        # Check if translation packages are installed
        installed = argostranslate.package.get_installed_packages()
        if installed:
            translation_ready = True
            print(f"✓ Translation models loaded: {len(installed)} language pairs")
        else:
            print("⚠ No translation models installed")
    except Exception as e:
        print(f"⚠ Translation initialization error: {e}")

class OfflineTranslator:
    """Offline translator using Argos Translate"""
    
    @staticmethod
    def translate(text, source_lang, target_lang):
        """Translate text offline"""
        try:
            installed_languages = argostranslate.translate.get_installed_languages()
            
            from_lang = None
            to_lang = None
            
            for lang in installed_languages:
                if lang.code == source_lang:
                    from_lang = lang
                if lang.code == target_lang:
                    to_lang = lang
            
            if from_lang is None or to_lang is None:
                return f"[Language pair {source_lang}->{target_lang} not available]"
            
            translation = from_lang.get_translation(to_lang)
            if translation is None:
                return f"[No translation path available]"
            
            return translation.translate(text)
        except Exception as e:
            return f"[Translation error: {str(e)}]"

class OfflineSpeechRecognizer:
    """Offline speech recognition using Vosk"""
    
    @staticmethod
    def recognize(audio_data, language='en'):
        """Recognize speech from audio data"""
        try:
            # Select appropriate model
            if language == 'zh':
                model = vosk_model_zh
            else:
                model = vosk_model_en
            
            if model is None:
                return "[Speech model not loaded]"
            
            # Create recognizer with 16kHz sample rate
            recognizer = KaldiRecognizer(model, 16000)
            recognizer.SetWords(True)
            
            # Process audio
            if recognizer.AcceptWaveform(audio_data):
                result = json.loads(recognizer.Result())
                return result.get('text', '')
            else:
                partial = json.loads(recognizer.PartialResult())
                return partial.get('partial', '')
                
        except Exception as e:
            return f"[Recognition error: {str(e)}]"

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for OpenShift"""
    status = {
        'status': 'healthy',
        'vosk_en': vosk_model_en is not None,
        'vosk_zh': vosk_model_zh is not None,
        'translation': translation_ready
    }
    return jsonify(status)

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
    """Handle text-only translation"""
    try:
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'zh')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            emit('translation_result', {'error': 'No text provided'})
            return
        
        translated = OfflineTranslator.translate(text, source_lang, target_lang)
        
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
    """Handle speech recognition from audio"""
    try:
        audio_base64 = data.get('audio', '')
        language = data.get('language', 'en')
        
        if not audio_base64:
            emit('recognition_result', {'error': 'No audio provided'})
            return
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Recognize speech
        recognized_text = OfflineSpeechRecognizer.recognize(audio_bytes, language)
        
        emit('recognition_result', {
            'text': recognized_text,
            'language': language
        })
    except Exception as e:
        emit('recognition_result', {'error': str(e)})

@socketio.on('translate_audio')
def handle_audio_translation(data):
    """Handle full audio -> recognition -> translation pipeline"""
    try:
        audio_base64 = data.get('audio', '')
        source_lang = data.get('source_lang', 'zh')
        target_lang = data.get('target_lang', 'en')
        
        if not audio_base64:
            emit('full_translation_result', {'error': 'No audio provided'})
            return
        
        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Recognize speech
        recognized_text = OfflineSpeechRecognizer.recognize(audio_bytes, source_lang)
        
        if not recognized_text or recognized_text.startswith('['):
            emit('full_translation_result', {
                'error': 'Could not recognize speech',
                'original': recognized_text
            })
            return
        
        # Translate
        translated_text = OfflineTranslator.translate(recognized_text, source_lang, target_lang)
        
        emit('full_translation_result', {
            'original': recognized_text,
            'translated': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
    except Exception as e:
        emit('full_translation_result', {'error': str(e)})

if __name__ == '__main__':
    # Initialize models before starting server
    initialize_models()
    
    # Run server
    port = int(os.getenv('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
