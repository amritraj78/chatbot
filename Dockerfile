FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies with caching
COPY requirements.txt .
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt

# Copy application files
COPY . .

# Expose port for Koyeb web service health check
EXPOSE 8000

CMD ["bash", "start"]
