"""
Real-Time Voice Translator (Chinese ↔ English) - Simplified Version
For physical customer meetings on PC with microphone

This version uses a simpler approach that's easier to set up.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import json

# Try to import optional dependencies
try:
    import speech_recognition as sr
    HAS_SR = True
except:
    HAS_SR = False

try:
    import pyttsx3
    HAS_TTS = True
except:
    HAS_TTS = False

# Try to import googletrans if available
try:
    from googletrans import Translator as GoogleTranslator
    HAS_GOOGLETRANS = True
except:
    HAS_GOOGLETRANS = False

# Fallback translation using free API
import urllib.request
import urllib.parse

class SimpleTranslator:
    """Simple translator using 100% open-source free translation services"""
    
    def __init__(self):
        # Use only open-source/free APIs (no Google)
        self.services = [
            self._translate_mymemory,    # Primary: Free, no key needed
            self._translate_libretranslate,  # Backup: Open-source
        ]
        
    def translate(self, text, source_lang, target_lang):
        """Translate text using available free APIs"""
        if not text or not text.strip():
            return ""
            
        # Try each service until one works
        for service in self.services:
            try:
                result = service(text, source_lang, target_lang)
                if result and not result.startswith("["):
                    return result
            except:
                continue
        
        return f"[Translation unavailable - check internet connection]"
    
    def _translate_mymemory(self, text, source_lang, target_lang):
        """Translate using MyMemory API (free, no key required)"""
        try:
            # MyMemory uses standard language codes
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
                return None
        except Exception as e:
            print(f"MyMemory error: {e}")
            return None
    
    def _translate_libretranslate(self, text, source_lang, target_lang):
        """Translate using LibreTranslate API"""
        try:
            params = {
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text",
                "api_key": ""
            }
            
            data = json.dumps(params).encode('utf-8')
            req = urllib.request.Request(
                "https://libretranslate.de/translate",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('translatedText', '')
        except Exception as e:
            print(f"LibreTranslate error: {e}")
            return None

class VoiceTranslator:
    def __init__(self):
        if HAS_SR:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None
            
        self.translator = SimpleTranslator()
        
        if HAS_TTS:
            try:
                self.tts_engine = pyttsx3.init()
            except:
                self.tts_engine = None
        else:
            self.tts_engine = None
            
        self.is_running = False
        self.source_lang = "zh"  # Default: Chinese to English
        self.target_lang = "en"
        
    def set_language_direction(self, direction):
        """Set translation direction"""
        if direction == "zh-en":
            self.source_lang = "zh"
            self.target_lang = "en"
        else:  # en-zh
            self.source_lang = "en"
            self.target_lang = "zh"
    
    def translate_text(self, text):
        """Translate text using LibreTranslate"""
        return self.translator.translate(text, self.source_lang, self.target_lang)
    
    def speak(self, text):
        """Convert text to speech"""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {str(e)}")
    
    def listen_and_translate(self, callback):
        """Listen to microphone and translate in real-time"""
        if not HAS_SR:
            callback("", "[SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio]")
            return
            
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise... Please wait")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                
                while self.is_running:
                    try:
                        # Listen with timeout
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                        
                        # Recognize speech using Google (free tier)
                        lang_code = "zh-CN" if self.source_lang == "zh" else "en-US"
                        recognized_text = self.recognizer.recognize_google(audio, language=lang_code)
                        
                        # Translate
                        translated_text = self.translate_text(recognized_text)
                        
                        # Send results to GUI
                        callback(recognized_text, translated_text)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        callback("", "[Could not understand audio]")
                    except sr.RequestError as e:
                        callback("", f"[Recognition service error: {e}]")
                    except Exception as e:
                        callback("", f"[Error: {str(e)}]")
        except OSError as e:
            callback("", f"[Microphone error: {e}. Check microphone connection.]")

class TranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Voice Translator - achildrenmile")
        self.root.geometry("800x600")
        
        self.translator = VoiceTranslator()
        self.listener_thread = None
        self.auto_clear = True  # Auto-clear after translation
        
        self.setup_ui()
        
        # Check dependencies
        self.check_dependencies()
        
    def check_dependencies(self):
        """Check which dependencies are available"""
        messages = []
        if not HAS_SR:
            messages.append("⚠️ SpeechRecognition not installed - voice input disabled")
            messages.append("   Install: pip install SpeechRecognition pyaudio")
        if not HAS_TTS:
            messages.append("⚠️ pyttsx3 not installed - voice output disabled")
            messages.append("   Install: pip install pyttsx3")
        
        if messages:
            status = "\n".join(messages)
            self.update_status(status, "orange")
        
    def setup_ui(self):
        # Control Frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Language direction selection
        ttk.Label(control_frame, text="Translation Direction:").pack(side=tk.LEFT, padx=5)
        
        self.direction_var = tk.StringVar(value="zh-en")
        directions = [("Chinese → English", "zh-en"), ("English → Chinese", "en-zh")]
        
        for text, value in directions:
            ttk.Radiobutton(control_frame, text=text, variable=self.direction_var, 
                          value=value, command=self.change_direction).pack(side=tk.LEFT, padx=5)
        
        # Manual input button
        self.manual_btn = ttk.Button(control_frame, text="Type Text", 
                                     command=self.show_manual_input)
        self.manual_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = ttk.Button(control_frame, text="Clear", 
                                    command=self.clear_display)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Start/Stop button
        self.toggle_btn = ttk.Button(control_frame, text="Start Listening", 
                                     command=self.toggle_listening)
        self.toggle_btn.pack(side=tk.LEFT, padx=20)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Ready", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Text display frame
        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Original speech
        ttk.Label(text_frame, text="Original Speech:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.original_text = scrolledtext.ScrolledText(text_frame, height=10, wrap=tk.WORD, 
                                                       font=("Arial", 11))
        self.original_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Translated speech
        ttk.Label(text_frame, text="Translation:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.translated_text = scrolledtext.ScrolledText(text_frame, height=10, wrap=tk.WORD, 
                                                         font=("Arial", 11))
        self.translated_text.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = """
        Instructions:
        1. Select translation direction (Chinese→English or English→Chinese)
        2. Click 'Start Listening' for voice input OR 'Type Text' for manual input
        3. Speak clearly into your microphone or type text
        4. Translation appears (screens auto-clear after each translation)
        5. Click 'Stop Listening' when done
        
        100% Open Source: MyMemory API (free, no API key required)
        """
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, text=instructions, font=("Arial", 8), foreground="gray").pack()
        
    def show_manual_input(self):
        """Show dialog for manual text input"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Manual Text Input")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Enter text to translate:", font=("Arial", 10, "bold")).pack(pady=10)
        
        input_text = scrolledtext.ScrolledText(dialog, height=8, wrap=tk.WORD, font=("Arial", 11))
        input_text.pack(fill=tk.BOTH, expand=True, padx=10)
        
        def translate_input():
            text = input_text.get("1.0", tk.END).strip()
            if text:
                # Clear previous translations
                if self.auto_clear:
                    self.clear_display()
                
                translated = self.translator.translate_text(text)
                self.update_display(text, translated)
                dialog.destroy()
        
        ttk.Button(dialog, text="Translate", command=translate_input).pack(pady=10)
        
    def change_direction(self):
        direction = self.direction_var.get()
        self.translator.set_language_direction(direction)
        if direction == "zh-en":
            self.update_status("Direction: Chinese → English", "blue")
        else:
            self.update_status("Direction: English → Chinese", "blue")
    
    def toggle_listening(self):
        if not HAS_SR:
            self.update_status("SpeechRecognition not installed! Use 'Type Text' button instead.", "red")
            return
            
        if not self.translator.is_running:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        self.translator.is_running = True
        self.toggle_btn.config(text="Stop Listening")
        self.update_status("Status: Listening...", "green")
        
        # Start listener thread
        self.listener_thread = threading.Thread(target=self.translator.listen_and_translate, 
                                               args=(self.update_display,), daemon=True)
        self.listener_thread.start()
    
    def stop_listening(self):
        self.translator.is_running = False
        self.toggle_btn.config(text="Start Listening")
        self.update_status("Status: Stopped", "red")
    
    def clear_display(self):
        """Clear both text displays"""
        self.original_text.delete("1.0", tk.END)
        self.translated_text.delete("1.0", tk.END)
    
    def update_display(self, original, translated):
        """Update text displays with new translation"""
        self.root.after(0, self._update_text_widgets, original, translated)
    
    def _update_text_widgets(self, original, translated):
        # Auto-clear before showing new translation
        if self.auto_clear:
            self.clear_display()
        
        if original:
            self.original_text.insert(tk.END, f"{original}\n")
            self.original_text.see(tk.END)
        
        if translated:
            self.translated_text.insert(tk.END, f"{translated}\n")
            self.translated_text.see(tk.END)
    
    def update_status(self, message, color):
        self.status_label.config(text=message, foreground=color)

def main():
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
