# Quick Start - Choose Your Version

## 🎯 Three Versions Available

### 1️⃣ Desktop Application (Recommended for Demo)
**Best for**: Immediate use, reliable voice recognition

```powershell
cd C:\voice-translator-prototype
python realtime_translator_simple.py
```

✅ **Works now** - Voice recognition confirmed working  
✅ **Simple** - Just run and use  
✅ **Reliable** - Best voice quality  

---

### 2️⃣ Web Application - Online (Easy Deployment)
**Best for**: Web interface, development, testing

```powershell
cd C:\voice-translator-prototype\web
python app_simple.py
```
Then open: **http://localhost:8080**

✅ **Web interface** - Access from any browser  
✅ **Text translation** - Works perfectly  
✅ **Voice translation** - Works (needs good microphone)  
⚠️ **Requires internet** - Uses Google + MyMemory APIs

---

### 3️⃣ Web Application - Offline (Production/Secure)
**Best for**: Air-gapped networks, production, high security

**Setup (one time)**:
```powershell
cd C:\voice-translator-prototype\web
pip install vosk argostranslate
python setup_offline.py  # Downloads ~300MB models
```

**Run**:
```powershell
python app_offline.py
```
Then open: **http://localhost:8081**

✅ **100% Offline** - No internet required after setup  
✅ **Air-gapped** - Works in isolated networks  
✅ **Secure** - No external APIs, all local processing  
✅ **OpenShift ready** - Deploy to Kubernetes  

---

## 📚 Full Documentation

- **VERSION_SUMMARY.md** - Complete version comparison
- **web/OFFLINE_SETUP.md** - Offline setup guide
- **TROUBLESHOOTING.md** - Voice debugging guide
