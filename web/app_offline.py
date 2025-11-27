"""
Real-Time Voice Translator - Fully Offline Web Version
No external APIs - uses Vosk (speech) + Argos Translate (translation)

Features:
- 100% offline operation (after initial model download)
- No internet required after setup
- Web-based interface
- Voice and text translation
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'achildrenmile-translator-offline'
socketio = SocketIO(app, cors_allowed_origins="*")

# Offline translator using Argos Translate
class OfflineTranslator:
    """Offline translator using Argos Translate"""
    
    def __init__(self):
        self.translators = {}
        self.setup_complete = False
        self._initialize_translators()
    
    def _initialize_translators(self):
        """Initialize Argos Translate with language packages"""
        try:
            import argostranslate.package
            import argostranslate.translate
            
            # Update package index
            print("Initializing offline translation models...")
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # Install required language pairs if not already installed
            required_pairs = [
                ('zh', 'en'),  # Chinese to English
                ('en', 'zh')   # English to Chinese
            ]
            
            installed_languages = argostranslate.package.get_installed_packages()
            
            for from_code, to_code in required_pairs:
                # Check if package is already installed
                found = False
                for installed_pkg in installed_languages:
                    if installed_pkg.from_code == from_code and installed_pkg.to_code == to_code:
                        found = True
                        print(f"✓ Translation model {from_code}→{to_code} already installed")
                        break
                
                if not found:
                    # Find and install the package
                    package_to_install = next(
                        filter(
                            lambda x: x.from_code == from_code and x.to_code == to_code,
                            available_packages
                        ),
                        None
                    )
                    
                    if package_to_install:
                        print(f"Installing translation model {from_code}→{to_code}...")
                        argostranslate.package.install_from_path(package_to_install.download())
                        print(f"✓ Installed {from_code}→{to_code}")
                    else:
                        print(f"✗ Warning: Could not find {from_code}→{to_code} package")
            
            self.setup_complete = True
            print("✓ Offline translation ready!")
            
        except ImportError:
            print("✗ Error: argostranslate not installed")
            print("   Run: pip install argostranslate")
            self.setup_complete = False
        except Exception as e:
            print(f"✗ Error initializing translator: {e}")
            import traceback
            traceback.print_exc()
            self.setup_complete = False
    
    def translate(self, text, source_lang, target_lang):
        """Translate text offline"""
        if not text or not text.strip():
            return ""
        
        if not self.setup_complete:
            return "[Offline translation not available - models not installed]"
        
        try:
            import argostranslate.translate
            
            # Translate
            translated = argostranslate.translate.translate(text, source_lang, target_lang)
            return translated
            
        except Exception as e:
            return f"[Translation error: {str(e)}]"

# Offline speech recognizer using Vosk
class OfflineSpeechRecognizer:
    """Offline speech recognition using Vosk"""
    
    def __init__(self):
        self.models = {}
        self.setup_complete = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize Vosk models for Chinese and English"""
        try:
            from vosk import Model
            
            # Model paths
            models_dir = os.path.expanduser("~/.vosk/models")
            
            model_configs = {
                'en': {
                    'path': os.path.join(models_dir, "vosk-model-small-en-us-0.15"),
                    'url': 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'
                },
                'zh': {
                    'path': os.path.join(models_dir, "vosk-model-small-cn-0.22"),
                    'url': 'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip'
                }
            }
            
            # Load models
            print("Initializing offline speech recognition models...")
            for lang, config in model_configs.items():
                if os.path.exists(config['path']):
                    try:
                        self.models[lang] = Model(config['path'])
                        print(f"✓ Loaded {lang} speech model from {config['path']}")
                    except Exception as e:
                        print(f"✗ Error loading {lang} model: {e}")
                else:
                    print(f"✗ Warning: {lang} model not found at {config['path']}")
                    print(f"   Download from: {config['url']}")
                    print(f"   Extract to: {config['path']}")
            
            if self.models:
                self.setup_complete = True
                print("✓ Offline speech recognition ready!")
            else:
                print("✗ No speech models loaded. Voice recognition will not work.")
                
        except ImportError:
            print("✗ Error: vosk not installed")
            print("   Run: pip install vosk")
            self.setup_complete = False
        except Exception as e:
            print(f"✗ Error initializing speech recognizer: {e}")
            import traceback
            traceback.print_exc()
            self.setup_complete = False
    
    def recognize(self, audio_data, language='en'):
        """Recognize speech from audio data"""
        if not self.setup_complete or language not in self.models:
            raise Exception(f"Speech model for {language} not available")
        
        try:
            from vosk import KaldiRecognizer
            import wave
            import io
            
            # Create recognizer for this language
            rec = KaldiRecognizer(self.models[language], 16000)
            
            # Process audio
            rec.AcceptWaveform(audio_data)
            result = rec.FinalResult()
            result_json = json.loads(result)
            
            return result_json.get('text', '')
            
        except Exception as e:
            raise Exception(f"Recognition error: {str(e)}")

# Initialize offline services
print("\n" + "="*60)
print("  Offline Voice Translator - Initializing")
print("="*60 + "\n")

translator = OfflineTranslator()
recognizer = OfflineSpeechRecognizer()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index_offline.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'translation': 'ready' if translator.setup_complete else 'unavailable',
        'speech_recognition': 'ready' if recognizer.setup_complete else 'unavailable',
        'models_loaded': {
            'translation': translator.setup_complete,
            'speech_en': 'en' in recognizer.models,
            'speech_zh': 'zh' in recognizer.models
        }
    })

@app.route('/status')
def status():
    """Get system status"""
    return jsonify({
        'translation_ready': translator.setup_complete,
        'speech_ready': recognizer.setup_complete,
        'models': {
            'speech_en': 'en' in recognizer.models,
            'speech_zh': 'zh' in recognizer.models
        }
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', {
        'message': 'Connected to offline translator service',
        'translation_ready': translator.setup_complete,
        'speech_ready': recognizer.setup_complete
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('translate_text')
def handle_text_translation(data):
    """Handle text translation (offline)"""
    try:
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'zh')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            emit('translation_result', {'error': 'No text provided'})
            return
        
        if not translator.setup_complete:
            emit('translation_result', {
                'error': 'Translation models not installed. Run setup first.'
            })
            return
        
        print(f"Translating offline: '{text}' ({source_lang}→{target_lang})")
        translated = translator.translate(text, source_lang, target_lang)
        print(f"Result: '{translated}'")
        
        emit('translation_result', {
            'original': text,
            'translated': translated,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
    except Exception as e:
        print(f"Translation error: {e}")
        emit('translation_result', {'error': str(e)})

@socketio.on('translate_audio')
def handle_audio_translation(data):
    """Handle audio translation (completely offline)"""
    try:
        import base64
        import io
        
        audio_base64 = data.get('audio', '')
        source_lang = data.get('source_lang', 'zh')
        target_lang = data.get('target_lang', 'en')
        
        if not audio_base64:
            emit('full_translation_result', {'error': 'No audio provided'})
            return
        
        if not recognizer.setup_complete:
            emit('full_translation_result', {
                'error': 'Speech recognition models not installed. Download Vosk models first.'
            })
            return
        
        if not translator.setup_complete:
            emit('full_translation_result', {
                'error': 'Translation models not installed. Install Argos Translate packages first.'
            })
            return
        
        print(f"\n[Offline] Processing audio: {source_lang}→{target_lang}")
        
        # Decode audio
        try:
            audio_bytes = base64.b64decode(audio_base64.split(',')[1] if ',' in audio_base64 else audio_base64)
            print(f"Decoded {len(audio_bytes)} bytes of WAV audio")
        except Exception as e:
            emit('full_translation_result', {'error': f'Audio decode error: {e}'})
            return
        
        # Extract raw PCM data from WAV (skip 44-byte header)
        pcm_data = audio_bytes[44:]
        
        # Recognize speech offline
        try:
            print(f"Recognizing speech offline ({source_lang})...")
            recognized_text = recognizer.recognize(pcm_data, source_lang)
            
            if not recognized_text or recognized_text.strip() == '':
                emit('full_translation_result', {
                    'error': 'Could not recognize speech. Please speak clearly and ensure Vosk models are installed.'
                })
                return
            
            print(f"✓ Recognized: '{recognized_text}'")
            
        except Exception as e:
            print(f"✗ Recognition error: {e}")
            emit('full_translation_result', {'error': f'Speech recognition failed: {e}'})
            return
        
        # Translate offline
        try:
            print(f"Translating offline: {source_lang}→{target_lang}...")
            translated_text = translator.translate(recognized_text, source_lang, target_lang)
            print(f"✓ Translated: '{translated_text}'")
            
        except Exception as e:
            print(f"✗ Translation error: {e}")
            emit('full_translation_result', {'error': f'Translation failed: {e}'})
            return
        
        # Send result
        emit('full_translation_result', {
            'original': recognized_text,
            'translated': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
        
    except Exception as e:
        print(f"\n✗ Error in offline audio translation:")
        import traceback
        traceback.print_exc()
        emit('full_translation_result', {'error': f'Server error: {str(e)}'})

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8081))
    
    print("\n" + "="*60)
    print("  Offline Voice Translator Web App")
    print("="*60)
    print(f"\n  URL: http://localhost:{port}")
    print(f"\n  Translation: {'✓ Ready' if translator.setup_complete else '✗ Not Ready'}")
    print(f"  Speech Recognition: {'✓ Ready' if recognizer.setup_complete else '✗ Not Ready'}")
    print(f"\n  Press Ctrl+C to stop\n")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
