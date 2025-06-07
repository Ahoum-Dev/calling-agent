FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Install LiveKit CLI via official installer script (auto-detects OS/arch)
RUN curl -sSL https://get.livekit.io/cli | bash

WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose API port
EXPOSE 5002

# Default command to run API server
CMD ["python", "api_server.py"] 