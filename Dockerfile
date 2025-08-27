FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    nmap \
    sqlmap \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_fastapi.txt .
RUN pip install --no-cache-dir -r requirements_fastapi.txt

# Install Django requirements for model access
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Wapiti via pip
RUN pip install --no-cache-dir wapiti3

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create media directory
RUN mkdir -p media

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Run entrypoint script
CMD ["./entrypoint.sh"]
