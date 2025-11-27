# Voice Translator - Web Version (OpenShift Deployment)

## 🌐 Fully Offline Web-Based Voice Translator

This is a containerized web version of the voice translator designed for deployment on **OpenShift** with **NO internet access required** after deployment.

### ✨ Features

- ✅ **100% Offline Operation** - Everything runs within the container
- ✅ **Web Interface** - No desktop application needed
- ✅ **Real-time Translation** - WebSocket-based live translation
- ✅ **Speech Recognition** - Offline Vosk models (English & Chinese)
- ✅ **Translation** - Offline Argos Translate models
- ✅ **OpenShift Ready** - Includes deployment templates
- ✅ **Auto-Clear Display** - Clean interface after each translation
- ✅ **Voice & Text Input** - Both modes supported

---

## 📦 What's Included in Container

### Speech Recognition (Vosk)
- English model: `vosk-model-small-en-us-0.15` (~40MB)
- Chinese model: `vosk-model-small-cn-0.22` (~42MB)
- Both downloaded during container build

### Translation (Argos Translate)
- Chinese → English model
- English → Chinese model
- Installed during container build

### All dependencies are bundled - no external internet access needed!

---

## 🚀 Local Testing (Before OpenShift)

### 1. Build Docker Image

```bash
cd web
docker build -t voice-translator:latest .
```

Build time: ~5-10 minutes (downloads models)
Image size: ~800MB-1GB

### 2. Run Locally

```bash
docker run -p 8080:8080 voice-translator:latest
```

### 3. Access Application

Open browser: `http://localhost:8080`

---

## ☁️ OpenShift Deployment

### Prerequisites

1. OpenShift cluster access
2. `oc` CLI installed
3. Project/namespace created

### Option 1: Using Template (Recommended)

```bash
# Login to OpenShift
oc login <your-cluster-url>

# Create project
oc new-project voice-translator

# Process and create template
oc process -f openshift-template.yaml | oc create -f -

# Monitor build
oc logs -f bc/voice-translator

# Get route URL
oc get route voice-translator
```

### Option 2: Manual Deployment

```bash
# Create app from Dockerfile
oc new-app https://your-git-repo/voice-translator.git \
  --context-dir=web \
  --name=voice-translator

# Expose service
oc expose svc/voice-translator

# Set resource limits
oc set resources dc/voice-translator \
  --limits=memory=2Gi,cpu=1 \
  --requests=memory=1Gi,cpu=500m
```

### Option 3: Binary Build (No Git Required)

```bash
# Create build config
oc new-build --name=voice-translator --binary --strategy=docker

# Start build from local directory
cd web
oc start-build voice-translator --from-dir=. --follow

# Create deployment
oc new-app voice-translator

# Expose service
oc expose svc/voice-translator

# Get URL
oc get route
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Application port |
| `VOSK_MODEL_EN` | `/app/models/vosk-model-small-en-us-0.15` | English speech model |
| `VOSK_MODEL_ZH` | `/app/models/vosk-model-small-cn-0.22` | Chinese speech model |

### Resource Requirements

**Minimum:**
- Memory: 1Gi
- CPU: 500m

**Recommended:**
- Memory: 2Gi
- CPU: 1000m (1 core)

**Storage:**
- Ephemeral storage: ~1GB for models

---

## 📊 Container Build Process

The Dockerfile performs these steps:

1. **Base Image**: Python 3.11-slim
2. **Install Dependencies**: wget, unzip, Python packages
3. **Download Argos Models**: Chinese ↔ English translation
4. **Download Vosk Models**: English & Chinese speech recognition
5. **Copy Application**: Flask app and templates
6. **Configure**: Set environment variables
7. **Ready**: Container includes everything offline

---

## 🎯 Usage Guide

### Web Interface Features

1. **Translation Direction**
   - Chinese → English
   - English → Chinese

2. **Voice Input**
   - Click "Start Listening"
   - Speak into microphone
   - Click "Stop Listening"
   - See translation

3. **Text Input**
   - Type text in bottom text area
   - Click "Translate"
   - See translation

4. **Auto-Clear**
   - Display clears automatically after each translation
   - Manual "Clear" button also available

### Health Check

```bash
curl http://<your-route>/health
```

Returns:
```json
{
  "status": "healthy",
  "vosk_en": true,
  "vosk_zh": true,
  "translation": true
}
```

---

## 🔒 Security & Air-Gapped Deployment

### For Completely Offline/Air-Gapped Environments:

1. **Build Container with Internet Access**
   ```bash
   docker build -t voice-translator:latest .
   ```

2. **Save Container Image**
   ```bash
   docker save voice-translator:latest | gzip > voice-translator.tar.gz
   ```

3. **Transfer to Air-Gapped Environment**
   - Copy `voice-translator.tar.gz` to offline network

4. **Load on Air-Gapped OpenShift**
   ```bash
   # On OpenShift node/bastion
   docker load < voice-translator.tar.gz
   
   # Tag for internal registry
   docker tag voice-translator:latest <registry>/voice-translator:latest
   
   # Push to internal registry
   docker push <registry>/voice-translator:latest
   ```

5. **Deploy from Internal Registry**
   ```bash
   oc new-app <registry>/voice-translator:latest
   oc expose svc/voice-translator
   ```

---

## 📈 Scaling & Performance

### Horizontal Scaling

```bash
# Scale to 3 replicas
oc scale dc/voice-translator --replicas=3
```

**Note:** Each pod loads models into memory (~1GB), so scale according to memory availability.

### Performance Tuning

- Use **larger Vosk models** for better accuracy (1-2GB each)
- Allocate **more CPU** for faster translation
- Use **persistent volumes** if you want to update models independently

---

## 🛠️ Troubleshooting

### Container Won't Start

```bash
# Check logs
oc logs -f dc/voice-translator

# Common issues:
# - Not enough memory (increase to 2Gi)
# - Models failed to download (check build logs)
```

### Models Not Loading

```bash
# Verify models in container
oc rsh dc/voice-translator
ls -lh /app/models/

# Should show:
# vosk-model-small-en-us-0.15/
# vosk-model-small-cn-0.22/
```

### Translation Not Working

```bash
# Check if Argos models installed
oc rsh dc/voice-translator
python3 -c "import argostranslate.package; print(argostranslate.package.get_installed_packages())"
```

### Microphone Not Working

- Browser must use **HTTPS** (OpenShift routes with TLS enabled)
- Check browser permissions for microphone access
- Try different browser (Chrome/Edge recommended)

---

## 📝 Model Customization

### Using Larger/Better Models

Edit `Dockerfile` to use larger Vosk models:

```dockerfile
# Replace small models with large ones
RUN cd /app/models && \
    wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip && \
    unzip vosk-model-en-us-0.22.zip && \
    wget https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip && \
    unzip vosk-model-cn-0.22.zip
```

**Trade-offs:**
- Better accuracy: 94-96% vs 90-92%
- Larger size: ~1.5GB per model vs ~40MB
- More memory: Needs 3-4GB RAM total

---

## 🔄 Updating the Application

```bash
# Rebuild
oc start-build voice-translator --follow

# Will automatically redeploy after build completes
```

---

## 📊 Monitoring

### Check Application Status

```bash
# Pod status
oc get pods

# Application logs
oc logs -f <pod-name>

# Resource usage
oc adm top pods
```

### Health Endpoint

Monitor at: `https://<your-route>/health`

---

## 🎉 Production Readiness Checklist

- [ ] Container builds successfully
- [ ] Models load correctly (check logs)
- [ ] Health endpoint returns healthy
- [ ] Web interface accessible via route
- [ ] Voice input works (requires HTTPS)
- [ ] Text translation works
- [ ] Resource limits configured
- [ ] Liveness/readiness probes working
- [ ] Multiple replicas tested (if scaling)
- [ ] Performance acceptable under load

---

## 📞 Support

For issues specific to:
- **OpenShift**: Check OpenShift documentation
- **Vosk Models**: https://alphacephei.com/vosk/models
- **Argos Translate**: https://github.com/argosopentech/argos-translate

---

## 🏷️ Version Information

- **Python**: 3.11
- **Flask**: 3.0.0
- **Vosk**: 0.3.45
- **Argos Translate**: 1.9.1
- **Socket.IO**: 5.3.5

---

## 🚀 Quick Start Summary

```bash
# 1. Build
docker build -t voice-translator web/

# 2. Test locally
docker run -p 8080:8080 voice-translator

# 3. Deploy to OpenShift
oc new-project voice-translator
oc new-build --name=voice-translator --binary --strategy=docker
cd web && oc start-build voice-translator --from-dir=. --follow
oc new-app voice-translator
oc expose svc/voice-translator
oc get route

# 4. Access
# Open the route URL in browser
```

**Done! 🎉**
