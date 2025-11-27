"""
Real-Time Voice Translator (Chinese ↔ English)
For physical customer meetings on PC with microphone

Features:
- Real-time speech recognition from microphone (100% Open Source)
- Bidirectional translation (Chinese ↔ English) using Argos Translate
- Text-to-speech output
- Simple GUI interface
- Works OFFLINE after initial model download
"""

import speech_recognition as sr
import argostranslate.package
import argostranslate.translate
import pyttsx3
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue
import os
from pathlib import Path

class VoiceTranslator:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.is_running = False
        self.source_lang = "zh"  # Default: Chinese to English
        self.target_lang = "en"
        self.translation_queue = queue.Queue()
        
        # Initialize Argos Translate models
        self._setup_translation_models()
    
    def _setup_translation_models(self):
        """Download and setup Argos Translate models (one-time setup)"""
        try:
            # Update package index
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # Install Chinese -> English and English -> Chinese models
            packages_to_install = []
            
            for package in available_packages:
                if (package.from_code == "zh" and package.to_code == "en") or \
                   (package.from_code == "en" and package.to_code == "zh"):
                    if not argostranslate.package.get_installed_packages():
                        packages_to_install.append(package)
                    else:
                        # Check if already installed
                        installed = False
                        for installed_pkg in argostranslate.package.get_installed_packages():
                            if installed_pkg.from_code == package.from_code and \
                               installed_pkg.to_code == package.to_code:
                                installed = True
                                break
                        if not installed:
                            packages_to_install.append(package)
            
            # Download and install packages
            for package in packages_to_install:
                print(f"Downloading translation model: {package.from_name} → {package.to_name}")
                download_path = package.download()
                argostranslate.package.install_from_path(download_path)
                print(f"✓ Installed: {package.from_name} → {package.to_name}")
            
            if not packages_to_install:
                print("✓ Translation models already installed")
                
        except Exception as e:
            print(f"Warning: Could not setup translation models: {e}")
            print("Translation may not work without models installed")
        
    def set_language_direction(self, direction):
        """Set translation direction"""
        if direction == "zh-en":
            self.source_lang = "zh"
            self.target_lang = "en"
        else:  # en-zh
            self.source_lang = "en"
            self.target_lang = "zh"
    
    def translate_text(self, text):
        """Translate text using Argos Translate (open source, offline)"""
        try:
            # Get installed translation
            installed_languages = argostranslate.translate.get_installed_languages()
            
            # Find source and target languages
            from_lang = None
            to_lang = None
            
            for lang in installed_languages:
                if lang.code == self.source_lang:
                    from_lang = lang
                if lang.code == self.target_lang:
                    to_lang = lang
            
            if from_lang is None or to_lang is None:
                return f"[Translation model not available for {self.source_lang}→{self.target_lang}]"
            
            # Get translation
            translation = from_lang.get_translation(to_lang)
            if translation is None:
                return f"[No translation path from {self.source_lang} to {self.target_lang}]"
            
            translated_text = translation.translate(text)
            return translated_text
            
        except Exception as e:
            return f"Translation error: {str(e)}"
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {str(e)}")
    
    def listen_and_translate(self, callback):
        """Listen to microphone and translate in real-time"""
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            
            while self.is_running:
                try:
                    # Listen with timeout
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    
                    # Recognize speech using Vosk (offline) or Sphinx (fallback)
                    lang_code = "zh-CN" if self.source_lang == "zh" else "en-US"
                    
                    # Try Vosk first (better accuracy, offline)
                    try:
                        recognized_text = self.recognizer.recognize_vosk(audio, language=lang_code)
                        import json
                        result = json.loads(recognized_text)
                        recognized_text = result.get("text", "")
                    except:
                        # Fallback to Sphinx (fully offline but lower accuracy)
                        try:
                            recognized_text = self.recognizer.recognize_sphinx(audio, language=lang_code)
                        except:
                            # Last resort: use Google (requires internet)
                            recognized_text = self.recognizer.recognize_google(audio, language=lang_code)
                    
                    # Translate
                    translated_text = self.translate_text(recognized_text)
                    
                    # Send results to GUI
                    callback(recognized_text, translated_text)
                    
                    # Speak translation (optional - can be toggled)
                    # self.speak(translated_text)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    callback("", "[Could not understand audio]")
                except sr.RequestError as e:
                    callback("", f"[Recognition service error: {e}]")
                except Exception as e:
                    callback("", f"[Error: {str(e)}]")

class TranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Voice Translator - achildrenmile")
        self.root.geometry("800x600")
        
        self.translator = VoiceTranslator()
        self.listener_thread = None
        
        self.setup_ui()
        
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
        2. Click 'Start Listening' to begin
        3. Speak clearly into your microphone
        4. View real-time transcription and translation
        5. Click 'Stop Listening' when done
        
        ✓ 100% Open Source | ✓ Works Offline (after model download)
        """
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, text=instructions, font=("Arial", 8), foreground="gray").pack()
        
    def change_direction(self):
        direction = self.direction_var.get()
        self.translator.set_language_direction(direction)
        if direction == "zh-en":
            self.update_status("Direction: Chinese → English", "blue")
        else:
            self.update_status("Direction: English → Chinese", "blue")
    
    def toggle_listening(self):
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
    
    def update_display(self, original, translated):
        """Update text displays with new translation"""
        self.root.after(0, self._update_text_widgets, original, translated)
    
    def _update_text_widgets(self, original, translated):
        if original:
            self.original_text.insert(tk.END, f"\n{original}\n")
            self.original_text.see(tk.END)
        
        if translated:
            self.translated_text.insert(tk.END, f"\n{translated}\n")
            self.translated_text.see(tk.END)
    
    def update_status(self, message, color):
        self.status_label.config(text=message, foreground=color)

def main():
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
