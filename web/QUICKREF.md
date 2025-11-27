# Quick Reference - OpenShift Deployment Commands

## Build & Deploy (Automated)

```powershell
# Windows PowerShell
cd C:\voice-translator-prototype\web
.\build-and-deploy.ps1

# Linux/Mac
cd /path/to/voice-translator-prototype/web
chmod +x build-and-deploy.sh
./build-and-deploy.sh
```

## Manual Commands

### 1. Build Image

```powershell
docker build -t voice-translator-offline:1.0 .
```

### 2. Test Locally

```powershell
docker run -d -p 8081:8081 --name test voice-translator-offline:1.0
Start-Process "http://localhost:8081"
docker logs -f test
docker stop test; docker rm test
```

### 3. Push to Registry

```powershell
# Docker Hub
docker login
docker tag voice-translator-offline:1.0 username/voice-translator-offline:1.0
docker push username/voice-translator-offline:1.0

# Quay.io
docker login quay.io
docker tag voice-translator-offline:1.0 quay.io/org/voice-translator-offline:1.0
docker push quay.io/org/voice-translator-offline:1.0
```

### 4. Deploy to OpenShift

```powershell
# Login
oc login https://your-cluster.com

# Update image in openshift-deployment.yaml, then:
oc apply -f openshift-deployment.yaml

# Check status
oc get pods -n translation-services
oc logs -f deployment/voice-translator-offline -n translation-services
```

### 5. Get Application URL

```powershell
$url = oc get route voice-translator-route -n translation-services -o jsonpath='{.spec.host}'
Start-Process "https://$url"
```

## Useful Commands

### Monitoring

```powershell
# Watch pods
oc get pods -n translation-services -w

# Resource usage
oc adm top pods -n translation-services

# Events
oc get events -n translation-services --sort-by='.lastTimestamp'

# Logs (all pods)
oc logs -f deployment/voice-translator-offline -n translation-services

# Logs (specific pod)
oc logs voice-translator-offline-xxx-yyy -n translation-services
```

### Scaling

```powershell
# Manual scale
oc scale deployment/voice-translator-offline --replicas=5 -n translation-services

# Check HPA
oc get hpa -n translation-services
oc describe hpa voice-translator-hpa -n translation-services
```

### Updates

```powershell
# Rolling update
oc set image deployment/voice-translator-offline translator=quay.io/org/voice-translator-offline:1.1 -n translation-services

# Watch rollout
oc rollout status deployment/voice-translator-offline -n translation-services

# Rollback
oc rollout undo deployment/voice-translator-offline -n translation-services
```

### Troubleshooting

```powershell
# Describe pod
oc describe pod <pod-name> -n translation-services

# Get previous logs (if crashed)
oc logs <pod-name> -n translation-services --previous

# Shell into pod
oc rsh <pod-name> -n translation-services

# Test health endpoint
oc exec <pod-name> -n translation-services -- curl http://localhost:8081/health

# Restart deployment
oc rollout restart deployment/voice-translator-offline -n translation-services
```

### Cleanup

```powershell
# Delete deployment
oc delete -f openshift-deployment.yaml

# Delete namespace (removes everything)
oc delete namespace translation-services
```

## Air-Gapped Deployment

```powershell
# 1. Save image on build machine (with internet)
docker save voice-translator-offline:1.0 -o translator.tar

# 2. Transfer translator.tar to air-gapped environment

# 3. Load image on OpenShift node
docker load -i translator.tar

# 4. Tag for internal registry
docker tag voice-translator-offline:1.0 image-registry.openshift-image-registry.svc:5000/translation-services/voice-translator-offline:1.0

# 5. Push to internal registry
docker push image-registry.openshift-image-registry.svc:5000/translation-services/voice-translator-offline:1.0

# 6. Deploy
oc apply -f openshift-deployment.yaml
```

## Health Check

```powershell
# Get route
$route = oc get route voice-translator-route -n translation-services -o jsonpath='{.spec.host}'

# Test health endpoint
curl "https://$route/health"

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

## Configuration Changes

```powershell
# Change replicas
oc patch deployment voice-translator-offline -p '{"spec":{"replicas":3}}' -n translation-services

# Update resource limits
oc set resources deployment/voice-translator-offline --limits=cpu=3,memory=6Gi -n translation-services

# Update environment variable
oc set env deployment/voice-translator-offline LOG_LEVEL=DEBUG -n translation-services
```

## Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Container image definition |
| `requirements_offline.txt` | Python dependencies |
| `openshift-deployment.yaml` | OpenShift resources (deployment, service, route, HPA) |
| `build-and-deploy.ps1` | Automated build & deploy (Windows) |
| `build-and-deploy.sh` | Automated build & deploy (Linux/Mac) |
| `DEPLOYMENT.md` | Full deployment guide |
| `.dockerignore` | Files to exclude from image |

## Pre-Deployment Checklist

- [ ] Docker installed and running
- [ ] `oc` CLI installed
- [ ] Logged in to OpenShift: `oc login`
- [ ] Logged in to container registry: `docker login`
- [ ] Updated registry URL in `openshift-deployment.yaml`
- [ ] Updated registry URL in `build-and-deploy.ps1` (if using)
- [ ] Template files exist in `templates/` directory
- [ ] `app_offline.py` present in web directory

## Post-Deployment Verification

1. **Pods running:**
   ```
   oc get pods -n translation-services
   # Both pods should be Running
   ```

2. **Health checks passing:**
   ```
   oc describe pod <pod-name> -n translation-services | Select-String "Liveness|Readiness"
   ```

3. **Application accessible:**
   ```
   Open https://voice-translator-route-translation-services.apps.your-cluster.com
   ```

4. **Translation working:**
   - Test text: "Hello" → "你好"
   - Test voice: Speak "Good morning" → "早上好"

5. **No external calls:**
   ```
   oc logs deployment/voice-translator-offline -n translation-services | Select-String "http|api|google"
   # Should see NO external HTTP calls
   ```
