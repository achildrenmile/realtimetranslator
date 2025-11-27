# Voice Translation Troubleshooting Guide

## Issue: "Could not understand the audio"

This error means the audio was successfully recorded and sent to the server, but Google's Speech Recognition API couldn't interpret the speech.

### Common Causes & Solutions

#### 1. **Background Noise**
- **Problem**: Microphone picking up too much ambient noise
- **Solution**: 
  - Move to a quieter environment
  - Use a headset with microphone instead of laptop mic
  - Close windows, turn off fans/AC during recording

#### 2. **Microphone Quality**
- **Problem**: Built-in laptop microphones often have poor quality
- **Solution**:
  - Use an external USB microphone or headset
  - Position microphone 6-12 inches from your mouth
  - Speak directly toward the microphone

#### 3. **Speaking Clarity**
- **Problem**: Speech too quiet, too fast, or unclear
- **Solution**:
  - Speak clearly and at a normal pace
  - Speak louder than normal conversation
  - Pause between sentences
  - Avoid speaking too fast

#### 4. **Wrong Language Selected**
- **Problem**: Speaking Chinese but "English → Chinese" is selected (or vice versa)
- **Current Settings**:
  - **Chinese → English**: Expects you to speak Chinese (中文)
  - **English → Chinese**: Expects you to speak English
- **Solution**: Verify the correct direction is selected before recording

#### 5. **Audio Duration**
- **Problem**: Recording too short (< 1 second) or too long (> 60 seconds)
- **Solution**:
  - Speak for 2-5 seconds minimum
  - Keep recordings under 30 seconds
  - For long content, break into shorter segments

### Testing Steps

1. **Test Microphone Access**
   - Click "Test Microphone" button
   - Grant permission when prompted
   - Verify "✓ Microphone is working!" appears

2. **Check Language Direction**
   - **For Chinese input**: Select "Chinese → English"
   - **For English input**: Select "English → Chinese"

3. **Record Test**
   - Click "Start Listening"
   - Status should show: "🎤 Recording Chinese (中文)..." or "🎤 Recording English..."
   - Speak clearly: "你好世界" (Chinese) or "Hello world" (English)
   - Click "Stop Listening" after 2-3 seconds

4. **Check Browser Console**
   - Press F12 → Console tab
   - Look for:
     - "Audio decoded - Duration: X.XX seconds" (should be > 1 second)
     - "WAV file created - Sample rate: 16000 Hz"
     - "Sending WAV audio for translation..."

5. **Check Server Terminal**
   - Look for:
     - "Decoded XXXXX bytes of audio data"
     - "Audio loaded successfully, duration: ~X.XXs"
     - "Attempting speech recognition with language: zh-CN" or "en-US"
   - If you see "✗ Speech recognition failed - audio not understood":
     - Read the tips printed in the terminal
     - Try speaking louder/clearer next time

### Alternative: Use Desktop App

If the web version continues to have issues, the **desktop app has more reliable voice recognition**:

```powershell
cd C:\voice-translator-prototype
python realtime_translator_simple.py
```

**Desktop App Advantages:**
- Uses system audio APIs (more reliable)
- Better noise cancellation
- Direct microphone access
- No browser audio conversion needed

### Quick Comparison

| Feature | Web App | Desktop App |
|---------|---------|-------------|
| Voice Input | ⚠️ Browser-dependent | ✅ Reliable |
| Audio Quality | ⚠️ Varies | ✅ Better |
| Setup | ✅ Just open browser | ⚠️ Requires Python |
| Deployment | ✅ OpenShift ready | ❌ Local only |
| Text Input | ✅ Works great | ✅ Works great |

### Recommendation

**For immediate customer demo:**
- Use **Desktop App** for voice translation (more reliable)
- Use **Web App** for text-only translation

**For production deployment:**
- Deploy **Web App** to OpenShift
- Consider adding external microphone requirement in documentation
- Test with high-quality headsets

### Testing Different Scenarios

#### Test 1: English to Chinese
```
1. Select: "English → Chinese"
2. Click "Start Listening"
3. Say clearly: "Hello, how are you today?"
4. Click "Stop Listening"
Expected: "你好，你今天怎么样？"
```

#### Test 2: Chinese to English
```
1. Select: "Chinese → English"  
2. Click "Start Listening"
3. Say clearly: "今天天气很好" (jīntiān tiānqì hěn hǎo)
4. Click "Stop Listening"
Expected: "The weather is very good today"
```

#### Test 3: Text Translation (Always Works)
```
1. Type in text box: "Thank you for your help"
2. Select: "English → Chinese"
3. Click "Translate Text"
Expected: "谢谢你的帮助"
```

### Advanced: Microphone Settings (Windows)

1. **Open Sound Settings**:
   - Right-click speaker icon in taskbar
   - Select "Sound settings"
   - Click "Input device properties"

2. **Adjust Microphone**:
   - Volume: 80-100%
   - Enable "Boost" if available
   - Disable "Automatic gain control" for consistency

3. **Test in Windows**:
   - Under "Test your microphone", speak
   - Blue bar should move when you talk
   - If not, microphone isn't working

### Contact Information

If issues persist after trying all solutions:
1. Check server terminal for specific error messages
2. Review browser console for client-side errors
3. Test with desktop app to isolate if it's a web-specific issue
4. Consider external microphone hardware upgrade
