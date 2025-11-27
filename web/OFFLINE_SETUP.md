# Offline Voice Translator - Setup Guide

## Overview

**Third Version**: 100% Offline Web App
- **No Internet Required** (after initial setup)
- **No External APIs** (Google, MyMemory, etc.)
- **Offline Speech Recognition**: Vosk models
- **Offline Translation**: Argos Translate
- **Perfect for**: Air-gapped environments, secure networks, OpenShift deployment

---

## Quick Start

### 1. Install Dependencies

```powershell
cd C:\voice-translator-prototype\web
pip install vosk argostranslate
```

### 2. Download Vosk Speech Models

**Option A: Automatic (requires internet once)**
```powershell
python setup_offline.py
```

**Option B: Manual Download**

Download these models and extract:

**English Model** (40MB):
- URL: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
- Extract to: `%USERPROFILE%\.vosk\models\vosk-model-small-en-us-0.15\`

**Chinese Model** (42MB):
- URL: https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip
- Extract to: `%USERPROFILE%\.vosk\models\vosk-model-small-cn-0.22\`

### 3. Install Translation Models

```powershell
python -c "import argostranslate.package; argostranslate.package.update_package_index(); available = argostranslate.package.get_available_packages(); en_zh = next(filter(lambda x: x.from_code == 'en' and x.to_code == 'zh', available)); argostranslate.package.install_from_path(en_zh.download()); zh_en = next(filter(lambda x: x.from_code == 'zh' and x.to_code == 'en', available)); argostranslate.package.install_from_path(zh_en.download())"
```

### 4. Copy Template File

```powershell
Copy-Item templates\index_simple.html templates\index_offline.html
```

Then edit `templates\index_offline.html` to change branding (see customization section below).

### 5. Run Offline Server

```powershell
python app_offline.py
```

Open browser at: http://localhost:8081

---

## How It Works

### Architecture

```
Browser Audio Recording
   ↓
Web Audio API (Convert to WAV)
   ↓
WebSocket → Server
   ↓
Vosk Speech Recognition (Offline)
   ↓
Argos Translate (Offline)
   ↓
WebSocket → Browser
   ↓
Display Translation
```

### Data Flow

**Text Translation:**
```
User types: "Hello" 
  → Argos Translate (en→zh) 
  → "你好"
```

**Voice Translation:**
```
1. Browser: Record audio → WAV format
2. Server: Vosk recognize speech → "Hello"
3. Server: Argos translate → "你好"
4. Browser: Display result
```

---

## File Structure

```
web/
├── app_offline.py          # Offline server (Vosk + Argos)
├── app_simple.py           # Online server (Google + MyMemory)
├── app.py                  # Full OpenShift version
├── templates/
│   ├── index_offline.html  # Offline web interface
│   ├── index_simple.html   # Online web interface
│   └── index.html          # Full OpenShift interface
└── OFFLINE_SETUP.md        # This file
```

---

## Customization

### Update Branding in index_offline.html

1. Change header color (green for offline):
```html
background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
```

2. Change title:
```html
<h1>🔒 achildrenmile Voice Translator - Offline</h1>
<p>100% Offline - Real-Time Chinese ↔ English Translation</p>
```

3. Update footer:
```html
<p>Translation: Argos Translate (Offline) | Speech: Vosk (Offline)</p>
<p>All processing happens locally - perfect for air-gapped environments.</p>
```

---

## Testing

### Test Text Translation (Offline)

1. Open http://localhost:8081
2. Type: "Hello world"
3. Select: "English → Chinese"
4. Click "Translate Text"
5. Should see: "你好世界"

**No internet needed!**

### Test Voice Translation (Offline)

1. Click "Test Microphone" (grant permission)
2. Select "English → Chinese"
3. Click "Start Listening"
4. Say: "Hello how are you"
5. Click "Stop Listening"
6. Should see: "你好你怎么样"

**No internet needed!**

---

## Comparison: Three Versions

| Feature | Desktop App | Web (Online) | Web (Offline) |
|---------|-------------|--------------|---------------|
| **Port** | N/A | 8080 | 8081 |
| **Speech** | Google API | Google API | Vosk (local) |
| **Translation** | MyMemory API | MyMemory API | Argos (local) |
| **Internet** | Required | Required | Not required* |
| **Setup** | Simple | Simple | Complex |
| **Accuracy** | High | High | Medium |
| **Speed** | Fast | Fast | Medium |
| **Security** | High | Low | Highest |
| **Air-gapped** | No | No | **Yes** |

*Internet required only for initial model download

---

## Troubleshooting

### "Speech model not found"

**Problem**: Vosk models not downloaded

**Solution**:
```powershell
# Create models directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.vosk\models"

# Download manually from:
# https://alphacephei.com/vosk/models/

# Extract .zip files to the models directory
```

### "Translation models not installed"

**Problem**: Argos Translate packages missing

**Solution**:
```powershell
python
>>> import argostranslate.package
>>> argostranslate.package.update_package_index()
>>> available = argostranslate.package.get_available_packages()
>>> # Install en→zh
>>> en_zh = next(filter(lambda x: x.from_code == 'en' and x.to_code == 'zh', available))
>>> argostranslate.package.install_from_path(en_zh.download())
>>> # Install zh→en
>>> zh_en = next(filter(lambda x: x.from_code == 'zh' and x.to_code == 'en', available))
>>> argostranslate.package.install_from_path(zh_en.download())
>>> exit()
```

### "Could not recognize speech"

**Problem**: Vosk model not matching language

**Causes**:
- Selected "Chinese → English" but speaking English
- Selected "English → Chinese" but speaking Chinese
- Vosk model files corrupted

**Solution**:
- Verify language direction matches what you're speaking
- Re-download Vosk models if corrupted
- Speak clearly and louder

### "Template not found"

**Problem**: index_offline.html doesn't exist

**Solution**:
```powershell
Copy-Item templates\index_simple.html templates\index_offline.html
```

Then customize the template (see Customization section above).

---

## Advantages of Offline Version

### Security
- ✅ No data sent to external APIs
- ✅ No internet required after setup
- ✅ Perfect for classified/sensitive environments
- ✅ Compliant with air-gapped network policies

### Privacy
- ✅ All processing happens locally
- ✅ No voice recordings sent to Google
- ✅ No text sent to MyMemory
- ✅ GDPR compliant (no data leaves premises)

### Reliability
- ✅ Works without internet
- ✅ No API rate limits
- ✅ No external service outages
- ✅ Predictable performance

### Deployment
- ✅ Can run in air-gapped OpenShift
- ✅ No API keys or credentials needed
- ✅ Self-contained Docker image
- ✅ No external dependencies at runtime

---

## Production Deployment

### Docker Build

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask flask-socketio vosk argostranslate

# Download Vosk models
RUN mkdir -p /root/.vosk/models && \
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
    unzip vosk-model-small-en-us-0.15.zip -d /root/.vosk/models/ && \
    rm vosk-model-small-en-us-0.15.zip && \
    wget https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip && \
    unzip vosk-model-small-cn-0.22.zip -d /root/.vosk/models/ && \
    rm vosk-model-small-cn-0.22.zip

# Install Argos translation models
RUN python -c "import argostranslate.package; argostranslate.package.update_package_index(); available = argostranslate.package.get_available_packages(); en_zh = next(filter(lambda x: x.from_code == 'en' and x.to_code == 'zh', available)); argostranslate.package.install_from_path(en_zh.download()); zh_en = next(filter(lambda x: x.from_code == 'zh' and x.to_code == 'en', available)); argostranslate.package.install_from_path(zh_en.download())"

# Copy application
COPY app_offline.py .
COPY templates/ templates/

EXPOSE 8081

CMD ["python", "app_offline.py"]
```

### Build and Run

```powershell
docker build -t translator-offline .
docker run -p 8081:8081 translator-offline
```

---

## Summary

You now have **three versions**:

1. **Desktop App** (`realtime_translator_simple.py`)
   - Best for: Quick demos, reliable voice input
   - Runs on: Windows with Python
   - Port: N/A (desktop GUI)

2. **Web App - Online** (`app_simple.py` on port 8080)
   - Best for: Easy setup, good translation quality
   - Runs on: Any OS with Python + browser
   - Requires: Internet connection

3. **Web App - Offline** (`app_offline.py` on port 8081)
   - Best for: Production, air-gapped networks, security
   - Runs on: Any OS with Python + browser
   - Requires: No internet after setup

Choose the version that fits your deployment requirements!
