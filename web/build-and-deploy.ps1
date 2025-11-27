# Build and Deploy Script for OpenShift
# Offline Voice Translator

# Configuration
$IMAGE_NAME = "voice-translator-offline"
$IMAGE_TAG = "1.0"
$REGISTRY = "quay.io/your-org"  # Change this to your registry
$NAMESPACE = "translation-services"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Offline Voice Translator - Build & Deploy" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Build Docker image
Write-Host "[1/6] Building Docker image..." -ForegroundColor Yellow
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker image built successfully`n" -ForegroundColor Green

# Step 2: Test image locally
Write-Host "[2/6] Testing image locally..." -ForegroundColor Yellow
docker run -d -p 8081:8081 --name translator-test ${IMAGE_NAME}:${IMAGE_TAG}

Start-Sleep -Seconds 15

$health = Invoke-RestMethod -Uri "http://localhost:8081/health" -ErrorAction SilentlyContinue

docker stop translator-test | Out-Null
docker rm translator-test | Out-Null

if ($health.status -eq "healthy") {
    Write-Host "✓ Image test passed`n" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Health check failed, but continuing...`n" -ForegroundColor Yellow
}

# Step 3: Tag for registry
Write-Host "[3/6] Tagging image for registry..." -ForegroundColor Yellow
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
Write-Host "✓ Image tagged: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}`n" -ForegroundColor Green

# Step 4: Push to registry
Write-Host "[4/6] Pushing image to registry..." -ForegroundColor Yellow
Write-Host "  (You may need to login: docker login ${REGISTRY})`n" -ForegroundColor Gray

docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker push failed! Did you login to the registry?" -ForegroundColor Red
    Write-Host "  Run: docker login ${REGISTRY}" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Image pushed to registry`n" -ForegroundColor Green

# Step 5: Update deployment YAML
Write-Host "[5/6] Updating deployment configuration..." -ForegroundColor Yellow

$deploymentFile = "openshift-deployment.yaml"
$content = Get-Content $deploymentFile -Raw

# Update image reference
$oldImage = "image: your-registry.io/voice-translator-offline:1.0"
$newImage = "image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
$content = $content -replace [regex]::Escape($oldImage), $newImage

Set-Content $deploymentFile -Value $content

Write-Host "✓ Deployment file updated`n" -ForegroundColor Green

# Step 6: Deploy to OpenShift
Write-Host "[6/6] Deploying to OpenShift..." -ForegroundColor Yellow
Write-Host "  (Make sure you're logged in: oc login)`n" -ForegroundColor Gray

# Check if logged in
$ocStatus = oc whoami 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Not logged in to OpenShift!" -ForegroundColor Red
    Write-Host "  Run: oc login https://your-cluster.com" -ForegroundColor Yellow
    exit 1
}

Write-Host "  Logged in as: $ocStatus" -ForegroundColor Gray

# Apply deployment
oc apply -f $deploymentFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Deployment applied successfully!`n" -ForegroundColor Green
    
    # Wait for rollout
    Write-Host "Waiting for rollout to complete..." -ForegroundColor Yellow
    oc rollout status deployment/voice-translator-offline -n $NAMESPACE --timeout=5m
    
    # Get route
    $route = oc get route voice-translator-route -n $NAMESPACE -o jsonpath='{.spec.host}' 2>$null
    
    if ($route) {
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "  Deployment Complete!" -ForegroundColor Cyan
        Write-Host "========================================`n" -ForegroundColor Cyan
        Write-Host "  Application URL: https://$route`n" -ForegroundColor Green
        Write-Host "  Check status:" -ForegroundColor White
        Write-Host "    oc get pods -n $NAMESPACE" -ForegroundColor Gray
        Write-Host "`n  View logs:" -ForegroundColor White
        Write-Host "    oc logs -f deployment/voice-translator-offline -n $NAMESPACE`n" -ForegroundColor Gray
    }
} else {
    Write-Host "`n✗ Deployment failed!" -ForegroundColor Red
    Write-Host "  Check the error messages above" -ForegroundColor Yellow
    exit 1
}
