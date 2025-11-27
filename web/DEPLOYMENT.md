# Deployment Guide - Offline Voice Translator to OpenShift

## Overview

This guide covers deploying the **100% offline** voice translator to OpenShift using Docker containerization.

**Key Features:**
- ✅ Zero external API dependencies at runtime
- ✅ All AI models included in container image
- ✅ Suitable for air-gapped environments
- ✅ Auto-scaling support
- ✅ Health checks and monitoring

---

## Prerequisites

### On Your Build Machine (Requires Internet)

1. **Docker Desktop** installed and running
2. **OpenShift CLI (oc)** installed
3. **Access to OpenShift cluster**
4. **Container registry** access (e.g., Quay.io, Docker Hub, internal registry)

### On OpenShift Cluster (Air-gapped OK)

- OpenShift 4.x cluster
- Namespace creation permissions
- At least 4GB RAM per pod
- No internet access required ✅

---

## Step 1: Build Docker Image

### 1.1 Navigate to Project Directory

```powershell
cd C:\voice-translator-prototype\web
```

### 1.2 Build the Container Image

**Note:** This step requires internet to download AI models (~300MB)

```powershell
# Build the image (takes 5-10 minutes)
docker build -t voice-translator-offline:1.0 .
```

**What happens during build:**
1. Installs Python 3.11 and dependencies
2. Downloads Vosk English model (40MB)
3. Downloads Vosk Chinese model (42MB)
4. Installs Argos Translate packages (200MB)
5. Copies application code
6. Verifies all models loaded correctly

**Expected output:**
```
Step 1/15 : FROM python:3.11-slim
Step 2/15 : WORKDIR /app
...
Step 13/15 : RUN python -c "import argostranslate.package; ..."
✓ Translation models installed
...
Step 15/15 : CMD ["python", "-u", "app_offline.py"]
Successfully built abc123def456
Successfully tagged voice-translator-offline:1.0
```

### 1.3 Verify Image

```powershell
# Check image size
docker images | findstr voice-translator

# Expected: ~2GB (includes Python + models)
```

### 1.4 Test Locally (Optional)

```powershell
# Run container locally
docker run -d -p 8081:8081 --name translator-test voice-translator-offline:1.0

# Test in browser
Start-Process "http://localhost:8081"

# Check logs
docker logs translator-test

# Expected:
# ✓ Offline translation ready!
# ✓ Offline speech recognition ready!
# Translation: ✓ Ready
# Speech Recognition: ✓ Ready

# Stop and remove test container
docker stop translator-test
docker rm translator-test
```

---

## Step 2: Push to Container Registry

### Option A: Docker Hub (Public/Private)

```powershell
# Login to Docker Hub
docker login

# Tag image
docker tag voice-translator-offline:1.0 your-dockerhub-username/voice-translator-offline:1.0

# Push
docker push your-dockerhub-username/voice-translator-offline:1.0
```

### Option B: Quay.io (Recommended for Enterprise)

```powershell
# Login to Quay
docker login quay.io

# Tag image
docker tag voice-translator-offline:1.0 quay.io/your-org/voice-translator-offline:1.0

# Push
docker push quay.io/your-org/voice-translator-offline:1.0
```

### Option C: OpenShift Internal Registry

```powershell
# Login to OpenShift
oc login https://your-openshift-cluster.com

# Get registry route
$REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')

# Login to registry
docker login -u $(oc whoami) -p $(oc whoami -t) $REGISTRY

# Tag image
docker tag voice-translator-offline:1.0 $REGISTRY/translation-services/voice-translator-offline:1.0

# Push
docker push $REGISTRY/translation-services/voice-translator-offline:1.0
```

### Option D: Air-Gapped Transfer

```powershell
# Save image to tar file
docker save voice-translator-offline:1.0 -o voice-translator-offline-1.0.tar

# Transfer file to air-gapped environment (USB, secure transfer, etc.)

# On air-gapped OpenShift node, load image:
docker load -i voice-translator-offline-1.0.tar

# Import to OpenShift
oc import-image voice-translator-offline:1.0 --from=voice-translator-offline:1.0 --confirm
```

---

## Step 3: Update Deployment Configuration

### 3.1 Edit openshift-deployment.yaml

Update the image reference in `openshift-deployment.yaml`:

```yaml
# Line 37-38, change:
image: your-registry.io/voice-translator-offline:1.0

# To your actual registry:
# For Docker Hub:
image: docker.io/your-username/voice-translator-offline:1.0

# For Quay:
image: quay.io/your-org/voice-translator-offline:1.0

# For OpenShift internal:
image: image-registry.openshift-image-registry.svc:5000/translation-services/voice-translator-offline:1.0
```

---

## Step 4: Deploy to OpenShift

### 4.1 Login to OpenShift

```powershell
# Login to your cluster
oc login https://your-openshift-cluster.com

# Or with token
oc login --token=sha256~xxxxx --server=https://your-cluster.com:6443
```

### 4.2 Create Namespace (if not exists)

```powershell
oc new-project translation-services
```

### 4.3 Deploy Application

```powershell
# Apply deployment configuration
oc apply -f openshift-deployment.yaml

# Expected output:
# namespace/translation-services configured
# deployment.apps/voice-translator-offline created
# service/voice-translator-svc created
# route.route.openshift.io/voice-translator-route created
# horizontalpodautoscaler.autoscaling/voice-translator-hpa created
```

### 4.4 Verify Deployment

```powershell
# Check pod status
oc get pods -n translation-services

# Expected:
# NAME                                      READY   STATUS    RESTARTS   AGE
# voice-translator-offline-xxx-yyy          1/1     Running   0          2m
# voice-translator-offline-xxx-zzz          1/1     Running   0          2m

# Check logs
oc logs -f deployment/voice-translator-offline -n translation-services

# Expected:
# Initializing offline translation models...
# ✓ Translation model zh→en already installed
# ✓ Translation model en→zh already installed
# ✓ Offline translation ready!
# Initializing offline speech recognition models...
# ✓ Loaded en speech model from /root/.vosk/models/vosk-model-small-en-us-0.15
# ✓ Loaded zh speech model from /root/.vosk/models/vosk-model-small-cn-0.22
# ✓ Offline speech recognition ready!
# Translation: ✓ Ready
# Speech Recognition: ✓ Ready
```

---

## Step 5: Access Application

### 5.1 Get Application URL

```powershell
# Get route URL
oc get route voice-translator-route -n translation-services -o jsonpath='{.spec.host}'

# Example output:
# voice-translator-route-translation-services.apps.your-cluster.com
```

### 5.2 Access in Browser

```powershell
# Get full URL
$URL = "https://$(oc get route voice-translator-route -n translation-services -o jsonpath='{.spec.host}')"

# Open in browser
Start-Process $URL
```

### 5.3 Test Application

1. **Test Text Translation:**
   - Input: "Hello world"
   - Direction: English → Chinese
   - Expected: "你好世界"

2. **Test Voice Translation:**
   - Click "Start Recording"
   - Say: "Good morning"
   - Click "Stop Recording"
   - Expected: "早上好"

3. **Verify Offline Operation:**
   - Check pod logs - should show NO external API calls
   - Monitor network - should see only internal cluster traffic

---

## Step 6: Monitoring & Scaling

### 6.1 Monitor Pods

```powershell
# Watch pod status
oc get pods -n translation-services -w

# Check resource usage
oc adm top pods -n translation-services

# Check HPA status
oc get hpa -n translation-services
```

### 6.2 View Logs

```powershell
# Stream logs from all pods
oc logs -f deployment/voice-translator-offline -n translation-services

# View logs from specific pod
oc logs voice-translator-offline-xxx-yyy -n translation-services

# View previous logs (if pod crashed)
oc logs voice-translator-offline-xxx-yyy -n translation-services --previous
```

### 6.3 Manual Scaling

```powershell
# Scale to 5 replicas
oc scale deployment/voice-translator-offline --replicas=5 -n translation-services

# Scale down to 1
oc scale deployment/voice-translator-offline --replicas=1 -n translation-services
```

### 6.4 Auto-Scaling

Auto-scaling is already configured via HPA:
- **Min replicas:** 2
- **Max replicas:** 10
- **CPU threshold:** 70%
- **Memory threshold:** 80%

```powershell
# Check HPA status
oc describe hpa voice-translator-hpa -n translation-services
```

---

## Step 7: Health Checks

### 7.1 Health Endpoint

The application exposes `/health` endpoint:

```powershell
# Check health from command line
$URL = oc get route voice-translator-route -n translation-services -o jsonpath='{.spec.host}'
curl "https://$URL/health"

# Expected response:
# {
#   "status": "healthy",
#   "translation": "ready",
#   "speech_recognition": "ready",
#   "models_loaded": {
#     "translation": true,
#     "speech_en": true,
#     "speech_zh": true
#   }
# }
```

### 7.2 Check Probe Status

```powershell
# View pod details (includes probe status)
oc describe pod <pod-name> -n translation-services

# Look for:
# Liveness:   http-get http://:8081/health
# Readiness:  http-get http://:8081/health
# Startup:    http-get http://:8081/health
```

---

## Troubleshooting

### Pod Not Starting

```powershell
# Check pod events
oc describe pod <pod-name> -n translation-services

# Common issues:
# - Insufficient memory: Increase resource limits
# - Image pull error: Check image name and registry access
# - Startup timeout: Increase startupProbe failureThreshold
```

### Pod Crashes / CrashLoopBackOff

```powershell
# View logs
oc logs <pod-name> -n translation-services --previous

# Common causes:
# - Models not loaded: Check Dockerfile build
# - Port already in use: Should not happen in OpenShift
# - Permission issues: Check security context
```

### Translation Not Working

```powershell
# Check pod logs for errors
oc logs deployment/voice-translator-offline -n translation-services | Select-String "error|Error|ERROR"

# Test health endpoint
curl https://your-route/health

# Restart pods
oc rollout restart deployment/voice-translator-offline -n translation-services
```

### High Memory Usage

```powershell
# Check current usage
oc adm top pods -n translation-services

# Models require ~2GB RAM per pod
# If OOMKilled, increase memory limits:
oc set resources deployment/voice-translator-offline --limits=memory=6Gi -n translation-services
```

### Slow Response Time

```powershell
# Check CPU usage
oc adm top pods -n translation-services

# If CPU throttling, increase CPU limits:
oc set resources deployment/voice-translator-offline --limits=cpu=3000m -n translation-services

# Or scale horizontally:
oc scale deployment/voice-translator-offline --replicas=5 -n translation-services
```

---

## Production Checklist

### Before Going Live

- [ ] Container image tested locally
- [ ] All models load successfully
- [ ] Health checks passing
- [ ] Resource limits configured appropriately
- [ ] HPA tested under load
- [ ] Route/ingress configured with TLS
- [ ] Monitoring and alerting set up
- [ ] Backup/recovery plan documented
- [ ] Air-gap operation verified (if required)

### Security Hardening

- [ ] Run as non-root user (optional, add to Dockerfile)
- [ ] Network policies configured (if needed)
- [ ] RBAC permissions reviewed
- [ ] Pod security policies applied
- [ ] Image scanning completed
- [ ] Secrets management (if storing API keys - not needed for offline)

### Performance Tuning

- [ ] Resource requests/limits optimized based on load testing
- [ ] HPA thresholds adjusted based on actual usage
- [ ] Pod disruption budget configured for high availability
- [ ] Persistent volumes (not needed - stateless app)

---

## Updates and Maintenance

### Rolling Update

```powershell
# Build new version
docker build -t voice-translator-offline:1.1 .

# Push to registry
docker push your-registry/voice-translator-offline:1.1

# Update deployment
oc set image deployment/voice-translator-offline translator=your-registry/voice-translator-offline:1.1 -n translation-services

# Watch rollout
oc rollout status deployment/voice-translator-offline -n translation-services
```

### Rollback

```powershell
# Rollback to previous version
oc rollout undo deployment/voice-translator-offline -n translation-services

# Rollback to specific revision
oc rollout undo deployment/voice-translator-offline --to-revision=2 -n translation-services
```

---

## Resource Requirements

### Per Pod

| Resource | Request | Limit | Notes |
|----------|---------|-------|-------|
| **CPU** | 500m | 2000m | Speech/translation CPU intensive |
| **Memory** | 2Gi | 4Gi | Models require ~2GB loaded |
| **Storage** | - | - | Ephemeral (models in image) |

### Cluster Total (2 replicas minimum)

- **CPU:** 1000m request, 4000m limit
- **Memory:** 4Gi request, 8Gi limit

### Scaling Considerations

- Each pod can handle ~10-20 concurrent users
- For 100 users: 5-10 pods recommended
- Cold start: ~15-20 seconds (model loading)
- Warm requests: <1 second response time

---

## Cost Optimization

### Resource Optimization

```powershell
# Use smaller models (already using "small" versions)
# Current: 82MB Vosk + 200MB Argos
# Alternative: Use tiny models if accuracy acceptable

# Reduce idle replicas
oc patch hpa voice-translator-hpa -n translation-services -p '{"spec":{"minReplicas":1}}'

# Set lower resource requests (if acceptable)
oc set resources deployment/voice-translator-offline --requests=cpu=250m,memory=1.5Gi -n translation-services
```

---

## Support

**For deployment issues:**
- Check logs: `oc logs deployment/voice-translator-offline -n translation-services`
- Review events: `oc get events -n translation-services --sort-by='.lastTimestamp'`
- Check documentation: README.md, OFFLINE_SETUP.md

**For application issues:**
- Test health endpoint: `curl https://your-route/health`
- Review OFFLINE_VERIFICATION.md for architecture details
- Check VERSION_SUMMARY.md for version comparison

---

## Next Steps

1. **Set up monitoring:** Prometheus, Grafana
2. **Configure alerts:** CPU/Memory thresholds
3. **Load testing:** Test with expected user load
4. **Disaster recovery:** Document backup/restore procedures
5. **Documentation:** Create runbook for operations team

---

**Deployment Complete!** 🎉

Your offline voice translator is now running on OpenShift with:
- ✅ Zero external API dependencies
- ✅ Auto-scaling enabled
- ✅ Health checks configured
- ✅ Production-ready setup

Access your application at: `https://voice-translator-route-translation-services.apps.your-cluster.com`
