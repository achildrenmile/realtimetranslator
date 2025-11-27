# Dockerfile for Offline Voice Translator
# 100% offline operation after build (no external APIs)
# Uses Vosk (speech recognition) + Argos Translate (translation)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_offline.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements_offline.txt

# Create directories for models
RUN mkdir -p /root/.vosk/models /root/.local/share/argos-translate/packages

# Download and install Vosk models (requires internet during build)
# English model (40MB)
RUN wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
    unzip vosk-model-small-en-us-0.15.zip -d /root/.vosk/models/ && \
    rm vosk-model-small-en-us-0.15.zip

# Chinese model (42MB)
RUN wget https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip && \
    unzip vosk-model-small-cn-0.22.zip -d /root/.vosk/models/ && \
    rm vosk-model-small-cn-0.22.zip

# Install Argos Translate language packages (requires internet during build)
RUN python -c "import argostranslate.package; \
    argostranslate.package.update_package_index(); \
    available = argostranslate.package.get_available_packages(); \
    en_zh = next(filter(lambda x: x.from_code == 'en' and x.to_code == 'zh', available)); \
    argostranslate.package.install_from_path(en_zh.download()); \
    zh_en = next(filter(lambda x: x.from_code == 'zh' and x.to_code == 'en', available)); \
    argostranslate.package.install_from_path(zh_en.download()); \
    print('✓ Translation models installed')"

# Copy application files
COPY app_offline.py .
COPY templates/ ./templates/

# Verify setup
RUN python -c "import vosk; import argostranslate; print('✓ All dependencies verified')"

# Expose port
EXPOSE 8081

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=8081
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8081/health', timeout=5)" || exit 1

# Run application
CMD ["python", "-u", "app_offline.py"]
