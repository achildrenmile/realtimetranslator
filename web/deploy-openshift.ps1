# Quick Build & Deploy Script for OpenShift

# Set variables
APP_NAME="voice-translator"
PROJECT_NAME="voice-translator"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Voice Translator - OpenShift Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if oc CLI is available
Write-Host "Checking OpenShift CLI..." -ForegroundColor Yellow
try {
    $ocVersion = oc version --client
    Write-Host "✓ OpenShift CLI found" -ForegroundColor Green
} catch {
    Write-Host "✗ OpenShift CLI not found. Please install 'oc' command." -ForegroundColor Red
    Write-Host "Download from: https://mirror.openshift.com/pub/openshift-v4/clients/ocp/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Current OpenShift context:" -ForegroundColor Yellow
oc whoami 2>&1
oc project 2>&1

Write-Host ""
$confirm = Read-Host "Continue with deployment? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Create project if it doesn't exist
Write-Host ""
Write-Host "Creating/switching to project: $PROJECT_NAME" -ForegroundColor Yellow
oc new-project $PROJECT_NAME 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Project may already exist, switching to it..." -ForegroundColor Yellow
    oc project $PROJECT_NAME
}

# Create build configuration
Write-Host ""
Write-Host "Creating build configuration..." -ForegroundColor Yellow
oc new-build --name=$APP_NAME --binary --strategy=docker 2>&1

# Start build from local directory
Write-Host ""
Write-Host "Starting build (this will take 5-10 minutes)..." -ForegroundColor Yellow
Write-Host "Downloading models and building container..." -ForegroundColor Gray
$webDir = Join-Path $PSScriptRoot "web"
Set-Location $webDir
oc start-build $APP_NAME --from-dir=. --follow

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Build completed successfully" -ForegroundColor Green

# Create application
Write-Host ""
Write-Host "Creating application..." -ForegroundColor Yellow
oc new-app $APP_NAME 2>&1

# Set resource limits
Write-Host ""
Write-Host "Setting resource limits..." -ForegroundColor Yellow
oc set resources dc/$APP_NAME --limits=memory=2Gi,cpu=1 --requests=memory=1Gi,cpu=500m

# Expose service
Write-Host ""
Write-Host "Exposing service..." -ForegroundColor Yellow
oc expose svc/$APP_NAME 2>&1

# Wait for deployment
Write-Host ""
Write-Host "Waiting for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
oc rollout status dc/$APP_NAME

# Get route
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$route = oc get route $APP_NAME -o jsonpath='{.spec.host}'
$url = "https://$route"

Write-Host "Application URL: " -ForegroundColor Yellow -NoNewline
Write-Host $url -ForegroundColor Cyan
Write-Host ""
Write-Host "Health Check: " -ForegroundColor Yellow -NoNewline
Write-Host "$url/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening in browser..." -ForegroundColor Yellow
Start-Process $url

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  oc logs -f dc/$APP_NAME          # View logs" -ForegroundColor White
Write-Host "  oc get pods                      # Check pod status" -ForegroundColor White
Write-Host "  oc scale dc/$APP_NAME --replicas=3  # Scale up" -ForegroundColor White
Write-Host ""
