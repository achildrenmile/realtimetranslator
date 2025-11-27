# Start the web application locally for testing
# Run this before deploying to OpenShift

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Voice Translator - Local Web Server" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to web directory
Set-Location C:\voice-translator-prototype\web

# Check if models exist (for local testing without full container build)
$modelsExist = Test-Path "models"
if (-not $modelsExist) {
    Write-Host "⚠ Vosk models not found locally." -ForegroundColor Yellow
    Write-Host "The app will still run but speech recognition won't work." -ForegroundColor Yellow
    Write-Host "Text translation will work if Argos models are installed." -ForegroundColor Gray
    Write-Host ""
    
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit 0
    }
}

Write-Host "Starting Flask web server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Application will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Set environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:PORT = "8080"

# Run the Flask app directly
python app.py
