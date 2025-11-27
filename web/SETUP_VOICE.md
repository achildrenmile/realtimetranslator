# Voice Recording Setup Guide

## Quick Start (For Voice Features)

The voice recording feature requires audio conversion libraries. Choose one of these options:

### Option 1: Install pydub + ffmpeg (Recommended)

```powershell
# 1. Install pydub
pip install pydub

# 2. Install ffmpeg (requires Administrator PowerShell)
# Run PowerShell as Administrator, then:
choco install ffmpeg -y

# Or download ffmpeg manually:
# - Download from https://www.gyan.dev/ffmpeg/builds/
# - Extract to C:\ffmpeg
# - Add C:\ffmpeg\bin to System PATH environment variable
```

### Option 2: Direct Audio Processing (Fallback)

If you can't install ffmpeg, the app will attempt direct audio processing, but it may have issues with some browsers' audio formats.

## Testing Voice Recording

1. Start the app:
```powershell
cd C:\voice-translator-prototype\web
python app_simple.py
```

2. Open browser at http://localhost:8080

3. Click "Test Microphone" button to verify microphone access

4. Click "Start Listening", speak clearly, then "Stop Listening"

## Troubleshooting

### "Could not understand audio"
- **Cause**: Audio format conversion issue or unclear speech
- **Solution**: 
  - Install pydub and ffmpeg (see above)
  - Speak more clearly and closer to microphone
  - Check microphone volume in Windows Sound Settings
  - Try Chrome or Edge browser (better MediaRecorder support)

### "pydub not available"
- **Cause**: pydub package not installed
- **Solution**: `pip install pydub`

### "ffmpeg not available"
- **Cause**: ffmpeg not installed or not in PATH
- **Solution**: 
  - Install via Chocolatey (as admin): `choco install ffmpeg -y`
  - Or download portable version and add to PATH

### Microphone Permission Denied
- **Cause**: Browser blocked microphone access
- **Solution**: 
  - Click the lock icon in browser address bar
  - Allow microphone permission for localhost
  - Refresh the page

### No Microphone Found
- **Cause**: No microphone device connected
- **Solution**:
  - Connect a microphone or headset
  - Set as default device in Windows Sound Settings (Input)

## Current Installation Status

Run this to check what's installed:

```powershell
# Check pydub
python -c "import pydub; print('pydub: OK')"

# Check ffmpeg
ffmpeg -version
```

## Alternative: Use Desktop App

If voice recording in the web app is problematic, use the desktop version instead:

```powershell
cd C:\voice-translator-prototype
python realtime_translator_simple.py
```

The desktop app has more reliable voice recognition using system audio APIs.
