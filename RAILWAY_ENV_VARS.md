# Railway Environment Variables Configuration

Add these in Railway Dashboard → Variables:

## Build Optimization
NIXPACKS_BUILD_TIME_CACHE=1
PIP_NO_CACHE_DIR=0
PIP_DISABLE_PIP_VERSION_CHECK=1

## Extended Timeout (if available)
RAILWAY_TIMEOUT=1800

## Python Optimization  
PYTHONUNBUFFERED=1
PYTHON_VERSION=3.11

## Reduce Memory Usage During Build
PIP_NO_BUILD_ISOLATION=1
