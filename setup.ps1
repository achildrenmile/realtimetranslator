# Quick Setup Script for Windows
# Installs all required dependencies for the Voice Translator
# 100% OPEN SOURCE VERSION

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "achildrenmile Voice Translator - Open Source Edition" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing open-source packages..." -ForegroundColor Yellow
Write-Host "(This may take 3-5 minutes for first-time setup)" -ForegroundColor Gray
Write-Host ""

# Install basic packages
try {
    pip install SpeechRecognition pyttsx3 argostranslate vosk pocketsphinx
    Write-Host "✓ Core packages installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install some packages" -ForegroundColor Red
    exit 1
}

# Special handling for PyAudio (often problematic on Windows)
Write-Host ""
Write-Host "Installing PyAudio (may require additional steps)..." -ForegroundColor Yellow
$pyaudioInstalled = $false

try {
    pip install pyaudio
    $pyaudioInstalled = $true
    Write-Host "✓ PyAudio installed successfully" -ForegroundColor Green
} catch {
    Write-Host "! PyAudio installation failed. Trying alternative method..." -ForegroundColor Yellow
    
    # Try pipwin
    try {
        pip install pipwin
        pipwin install pyaudio
        $pyaudioInstalled = $true
        Write-Host "✓ PyAudio installed via pipwin" -ForegroundColor Green
    } catch {
        Write-Host "! Could not install PyAudio automatically" -ForegroundColor Yellow
    }
}

# Download Vosk models
Write-Host ""
Write-Host "Downloading Vosk speech recognition models..." -ForegroundColor Yellow
Write-Host "(This is a one-time download, ~50MB per language)" -ForegroundColor Gray

$voskDir = "$HOME\.vosk\models"
New-Item -ItemType Directory -Force -Path $voskDir | Out-Null

# Download English model
$enModelUrl = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
$enModelZip = "$voskDir\vosk-model-small-en-us-0.15.zip"
$enModelDir = "$voskDir\vosk-model-small-en-us-0.15"

if (!(Test-Path $enModelDir)) {
    Write-Host "Downloading English model..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $enModelUrl -OutFile $enModelZip
        Expand-Archive -Path $enModelZip -DestinationPath $voskDir -Force
        Remove-Item $enModelZip
        Write-Host "✓ English model downloaded" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Could not download English model automatically" -ForegroundColor Yellow
        Write-Host "  Download manually from: https://alphacephei.com/vosk/models" -ForegroundColor White
    }
} else {
    Write-Host "✓ English model already exists" -ForegroundColor Green
}

# Download Chinese model
$zhModelUrl = "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
$zhModelZip = "$voskDir\vosk-model-small-cn-0.22.zip"
$zhModelDir = "$voskDir\vosk-model-small-cn-0.22"

if (!(Test-Path $zhModelDir)) {
    Write-Host "Downloading Chinese model..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $zhModelUrl -OutFile $zhModelZip
        Expand-Archive -Path $zhModelZip -DestinationPath $voskDir -Force
        Remove-Item $zhModelZip
        Write-Host "✓ Chinese model downloaded" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Could not download Chinese model automatically" -ForegroundColor Yellow
        Write-Host "  Download manually from: https://alphacephei.com/vosk/models" -ForegroundColor White
    }
} else {
    Write-Host "✓ Chinese model already exists" -ForegroundColor Green
}

# Installation summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Installation Summary" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

if ($pyaudioInstalled) {
    Write-Host "✓ All packages installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the translator:" -ForegroundColor Green
    Write-Host "  python realtime_translator_pc.py" -ForegroundColor White
} else {
    Write-Host "⚠ Almost complete - PyAudio needs manual installation" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio" -ForegroundColor White
    Write-Host "2. Download the .whl file matching your Python version" -ForegroundColor White
    Write-Host "3. Run: pip install <downloaded-file>.whl" -ForegroundColor White
    Write-Host ""
    Write-Host "Your Python version: $pythonVersion" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Open Source Components:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✓ Argos Translate - Offline translation (MIT License)" -ForegroundColor White
Write-Host "✓ Vosk - Speech recognition (Apache 2.0 License)" -ForegroundColor White
Write-Host "✓ PocketSphinx - Fallback speech recognition (BSD License)" -ForegroundColor White
Write-Host "✓ pyttsx3 - Text-to-speech (MPL 2.0 License)" -ForegroundColor White
Write-Host ""
Write-Host "Works 100% offline after initial model download!" -ForegroundColor Green
Write-Host ""
