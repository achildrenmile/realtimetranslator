# Quick Deploy Guide - Choose Your Platform

## ⚠️ Fly.io Issue Resolution

Your error indicates CPU limit reached. **Solutions:**

### Option A: Use Shared CPU (Free Tier)
```powershell
cd C:\privrepo\realtimetranslator\web
fly scale count 1
fly scale memory 512
fly scale vm shared-cpu-1x
```

### Option B: Delete old apps to free resources
```powershell
fly apps list
fly apps destroy <old-app-name>
```

---

## ✅ Recommended: Railway.app (Easiest)

**Why Railway:**
- ✅ $5 free credit/month
- ✅ No CPU limits on free tier
- ✅ Auto-detects Python
- ✅ One-click deploy from GitHub

### Deploy Steps:
1. Go to: https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `achildrenmile/realtimetranslator`
4. Railway automatically:
   - Detects Python 3.11
   - Installs dependencies
   - Downloads models (~500MB)
   - Starts app on port 8081
5. Get public URL: `https://voice-translator.up.railway.app`

**Estimated build time:** 8-10 minutes (downloading models)

---

## ✅ Alternative: Render.com (Also Easy)

**Deploy Button:** 
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/achildrenmile/realtimetranslator)

### Manual Steps:
1. Go to: https://render.com
2. New → Web Service
3. Connect GitHub: `achildrenmile/realtimetranslator`
4. Settings:
   - **Root Directory:** `web`
   - **Build Command:** `pip install -r requirements_offline.txt && python install_models.py`
   - **Start Command:** `python app_offline.py`
   - **Instance Type:** Free (or Starter $7/mo for 2GB RAM)
5. Click "Create Web Service"

**Note:** Free tier may be slow due to 512MB RAM limit. Models need ~500MB.

---

## ✅ Best for Heavy Models: Hugging Face Spaces (Free Forever)

**Perfect for ML projects with large models!**

### Steps:
1. Create account: https://huggingface.co/join
2. Create new Space: https://huggingface.co/new-space
3. Settings:
   - **Name:** `voice-translator-offline`
   - **SDK:** Docker
   - **Hardware:** CPU (free)
4. Clone your space:
```powershell
git clone https://huggingface.co/spaces/YOUR_USERNAME/voice-translator-offline
cd voice-translator-offline
```
5. Copy files:
```powershell
Copy-Item C:\privrepo\realtimetranslator\web\* -Recurse
git add .
git commit -m "Add offline voice translator"
git push
```

**Pros:**
- Free forever (no credit card)
- Handles large models well
- ML community visibility
- No cold starts

---

## ✅ If You Must Use Fly.io

### Fix the CPU limit issue:

1. **Check current apps:**
```powershell
fly apps list
```

2. **Scale down or delete old apps:**
```powershell
# Scale down to 1 shared CPU
fly scale vm shared-cpu-1x --app OLD_APP_NAME

# Or delete
fly apps destroy OLD_APP_NAME
```

3. **Create with minimal resources:**
```powershell
cd C:\privrepo\realtimetranslator\web
fly launch --name voice-translator --vm-size shared-cpu-1x --vm-memory 512
```

4. **Deploy:**
```powershell
fly deploy
```

---

## Quick Comparison

| Platform | Free Tier | Setup Time | Best For |
|----------|-----------|------------|----------|
| **Railway** ⭐ | $5/month credit | 2 min | Quick demo |
| **Render** | 512MB RAM | 3 min | Simple apps |
| **HF Spaces** 🏆 | Unlimited | 5 min | ML/AI showcase |
| **Fly.io** | 3 VMs, 256MB | 5 min | Production |
| **Replit** | Limited resources | 1 min | Code demo |

---

## My Recommendation: Railway.app

**Why:**
1. Fastest setup (2 minutes)
2. No CPU/core limits
3. $5 credit = ~500 hours/month on small instance
4. Auto-deploys from GitHub
5. Great for demos

**Deploy now:**
```
https://railway.app/new/template?template=https://github.com/achildrenmile/realtimetranslator
```

Would you like me to set up Railway deployment for you?
