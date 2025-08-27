FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (note: Wapiti installed via pip, not apt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    nmap sqlmap netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Install Wapiti via pip (package name: wapiti3)
RUN pip install --no-cache-dir wapiti3

COPY . .
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]