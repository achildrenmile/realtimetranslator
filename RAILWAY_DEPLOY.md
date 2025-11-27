# Railway Deployment - Quick Guide

## ✅ Optimized for Railway Free Tier

The app is now configured to work within Railway's free tier limits:

### Image Size Optimization
- **Before:** 7.8 GB (exceeded 4 GB limit)
- **After:** <1 GB (models download at runtime)

### How It Works
1. **Build Phase** (~2 minutes):
   - Installs Python dependencies
   - Creates small Docker image (<1 GB)

2. **First Startup** (~3-5 minutes):
   - Downloads Vosk models (82 MB)
   - Downloads Argos Translate models (200 MB)
   - Models are cached in persistent storage

3. **Subsequent Startups** (~10 seconds):
   - Uses cached models
   - Fast startup

## Deploy to Railway

### Option 1: One-Click Deploy
1. Visit: **https://railway.app/new**
2. Click "Deploy from GitHub repo"
3. Select: `achildrenmile/realtimetranslator`
4. Wait ~8 minutes total (2 min build + 5 min first startup)
5. Access your URL

### Option 2: Railway CLI
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

## Configuration

### Automatic Settings
Railway automatically detects:
- ✅ Python 3.11
- ✅ Dependencies from `requirements.txt`
- ✅ Start command from `nixpacks.toml`

### Environment Variables (Optional)
Add these in Railway dashboard if needed:
- `PORT` - Railway sets automatically (default: 8081)
- `PYTHONUNBUFFERED=1` - See logs in real-time

## Expected Timeline

| Phase | Duration | What Happens |
|-------|----------|--------------|
| Build | 2-3 min | Install Python packages |
| Deploy | 30 sec | Start container |
| Model Download | 3-5 min | Download Vosk + Argos models |
| **Ready** | **6-8 min** | App accessible |

## First Access

When you first visit your Railway URL:
- You might see a loading screen
- Models are downloading in background
- Check Railway logs to see progress
- Once you see "✓ Offline speech recognition ready!" - it's live!

## Resource Usage (Free Tier)

- **Memory:** ~800 MB (well within 8 GB limit)
- **Storage:** ~500 MB for models
- **Bandwidth:** Minimal (all processing is local)
- **CPU:** Shared (sufficient for demos)

## Monitoring

View logs in Railway dashboard:
```
Initializing offline translation models...
✓ Translation model zh→en already installed
✓ Translation model en→zh already installed
✓ Offline translation ready!

Initializing offline speech recognition models...
✓ Loaded en speech model
✓ Loaded zh speech model
✓ Offline speech recognition ready!

URL: http://0.0.0.0:PORT
```

## Troubleshooting

### Build fails with "image too large"
- ✅ Fixed! Models now download at runtime

### "ModuleNotFoundError" at startup
- Railway is still installing dependencies
- Wait 1-2 more minutes

### Models downloading every restart
- Add Railway volume: Settings → Add Volume
- Mount to: `/root/.vosk/models` and `/root/.local/share`

### Slow response times
- First request after idle: ~30 sec (Railway free tier sleeps)
- Upgrade to Hobby plan ($5/mo) for always-on

## Production Recommendations

For production use:
1. **Upgrade to Hobby plan** ($5/mo)
   - No sleep after inactivity
   - Better performance
   - More memory

2. **Add persistent volume**
   - Models persist across deployments
   - Faster restarts

3. **Set custom domain**
   - Professional appearance
   - SSL included

## Cost Estimate

**Free Tier:**
- $5 credit/month
- Enough for ~500 hours
- Good for demos/testing

**Hobby Plan:**
- $5/month base
- Always-on
- Better for production

## Next Steps

1. ✅ Deploy to Railway
2. Wait for models to download
3. Test at your Railway URL
4. Share with stakeholders
5. Consider upgrade for production

---

**Live Demo:** Your app will be at `https://YOUR-APP-NAME.up.railway.app`

Need help? Check Railway logs or the main README.md
