# Fix Railway "Image Too Large" Error

## The Problem
Railway cached the old build that downloaded models during build time (7.8 GB).

## The Solution - Clear Railway Cache

### In Railway Dashboard:

1. **Go to your deployment**
2. Click **Settings** tab
3. Scroll to **Danger Zone**
4. Click **"Clear Build Cache"**
5. Click **"Redeploy"**

OR

1. **Delete the current deployment**
2. **Create a new deployment** from GitHub

### The New Build Will:
- ✅ Only install Python packages (<1 GB)
- ✅ Download models on first startup (not during build)
- ✅ Complete successfully

## Verification

After redeploying, check the build logs. You should see:

```
Building...
Installing Python 3.11
Installing dependencies from requirements.txt
Build complete! (< 1 GB)
```

Then on first startup:
```
Initializing offline translation models...
Downloading models... (this happens at runtime now)
✓ Offline translation ready!
```

## Important Settings for Railway

If you want to add a **persistent volume** to keep models between restarts:

1. Go to **Settings** → **Volumes**
2. Click **"New Volume"**
3. Mount path: `/root/.vosk/models`
4. Click **"Add"**
5. Repeat for `/root/.local/share/argos-translate`

This way models download once and persist across deploys.

## Alternative: Start Fresh

If clearing cache doesn't work:

1. Delete the current Railway service
2. Go to https://railway.app/new
3. Connect `achildrenmile/realtimetranslator`
4. Fresh deployment will use new config

The repository is already optimized - you just need to clear Railway's old cache!
