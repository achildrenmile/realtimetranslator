# Render.com Deployment Fix

## Problem
Render is running \gunicorn app:app\ instead of the correct command from render.yaml.

**Root Cause:** When you manually create a service in Render, it doesn't automatically use render.yaml. The dashboard settings override the YAML file.

## Solution Options

### Option 1: Update Existing Service (Quick Fix - 2 minutes)

1. **Go to Render Dashboard**
   - URL: https://dashboard.render.com
   - Log in to your account

2. **Select Your Service**
   - Click on \oice-translator-offline\ service

3. **Go to Settings**
   - Click the "Settings" tab in the left sidebar

4. **Update Start Command**
   - Scroll to "Start Command" field
   - **Replace with:**
   \\\
   cd web && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:\$PORT app_offline:app
   \\\

5. **Save and Deploy**
   - Click "Save Changes" button at bottom
   - Render will automatically redeploy with the new command
   - Wait 2-3 minutes for deployment

6. **Verify**
   - Check logs - should see "Starting gunicorn" in web/ directory
   - No more "ModuleNotFoundError: No module named 'app'"

---

### Option 2: Deploy with Blueprint (Clean Start - 5 minutes)

If Option 1 doesn't work or you want a fresh start:

1. **Delete Current Service**
   - Go to service settings
   - Scroll to bottom
   - Click "Delete Service"
   - Confirm deletion

2. **Deploy from GitHub with Blueprint**
   - Go to: https://dashboard.render.com/select-repo
   - Connect your GitHub account if needed
   - Select: \childrenmile/realtimetranslator\
   - Render will detect \ender.yaml\ automatically
   - Click "Apply" to create service with correct settings

3. **Wait for Deployment**
   - Build: ~3-5 minutes (installing ML packages)
   - First startup: ~5 minutes (downloading Vosk + Argos models ~280MB)
   - Total: ~10 minutes for first deployment

---

## What the Correct Command Does

\\\ash
cd web && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:\ app_offline:app
\\\

- \cd web\ - Navigate to web directory where app_offline.py is located
- \gunicorn\ - Production WSGI server (required by Render)
- \--worker-class eventlet\ - Async worker for WebSocket support (Flask-SocketIO)
- \-w 1\ - Single worker (eventlet doesn't support multiple workers)
- \--bind 0.0.0.0:\\ - Bind to all interfaces on Render's assigned port
- \pp_offline:app\ - Import \pp\ variable from \pp_offline.py\ module

---

## Expected Deployment Timeline

| Phase | Time | What's Happening |
|-------|------|------------------|
| Build | 3-5 min | Installing Python packages (Flask, vosk, argostranslate, eventlet) |
| First Startup | 5-8 min | Downloading Vosk models (82MB) + Argos packages (200MB) |
| Ready | - | Service accessible at https://voice-translator-offline.onrender.com |

**Subsequent Deployments:** ~3 minutes (models already cached)

---

## Verification Steps

Once deployed, check the logs for these success indicators:

\\\
 "Starting gunicorn"
 "Booting worker with pid"
 "Downloading Vosk model" (first time only)
 "Installing Argos Translate package" (first time only)
 "OfflineTranslator initialized"
 "OfflineSpeechRecognizer initialized"
 "Running on http://0.0.0.0:XXXX"
\\\

**Error Indicators:**
 "ModuleNotFoundError: No module named 'app'" - Wrong start command
 "gunicorn app:app" - Not using render.yaml settings
 "No such file or directory: app.py" - Not in web/ directory

---

## Troubleshooting

### Issue: Still seeing "gunicorn app:app" error

**Cause:** Render cached the old start command

**Fix:**
1. Go to service Settings
2. Click "Manual Deploy"  "Clear build cache & deploy"
3. Wait for rebuild (this forces Render to use new settings)

### Issue: "Build succeeded, but start command failed"

**Cause:** Render using Python 3.13 (eventlet incompatible with gevent)

**Fix:**
1. In Settings, add Environment Variable:
   - Key: \PYTHON_VERSION\
   - Value: \3.11.0\
2. Redeploy

### Issue: Deployment takes forever (>15 minutes)

**Cause:** Models downloading during startup (expected on first deployment)

**Fix:** Wait patiently. Check logs to see download progress. Once complete, models are cached for future deployments.

---

## Alternative: Deploy to Render Button

Add this to README.md for one-click deploys:

\\\markdown
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/achildrenmile/realtimetranslator)
\\\

This button uses render.yaml automatically, ensuring correct configuration.

