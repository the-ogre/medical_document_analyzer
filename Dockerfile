# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    wget \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY setup.py .
COPY medical_analyzer ./medical_analyzer
RUN pip install --no-cache-dir -e ".[tesseract]"

# Create necessary directories
RUN mkdir -p /app/medical_analyzer/data /app/medical_analyzer/static /app/medical_analyzer/models

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OCR_ENGINE=tesseract \
    TESSERACT_CMD=tesseract \
    LLM_BACKEND=ollama

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "medical_analyzer.app:app", "--host", "0.0.0.0", "--port", "8000"]