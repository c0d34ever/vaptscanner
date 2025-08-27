# VAPT Platform (Django + Celery + ZAP)

## Prerequisites
- Python 3.11+
- Redis (for Celery broker/result)
- OWASP ZAP (daemon/API enabled)

## Setup
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Initialize DB
python manage.py makemigrations
python manage.py migrate

# Start ZAP (Windows example)
& "C:\\Program Files\\OWASP\\Zed Attack Proxy\\zap.bat" -daemon -config api.disablekey=true

# Start worker and web
celery -A vapt_platform worker --loglevel=info
python manage.py runserver
```

Then open http://127.0.0.1:8000 to use the UI.

## One-command Docker deploy (Linux VPS)

Prereqs: Docker and Docker Compose

```bash
export VAPT_API_KEY="your-strong-key"
docker compose up -d --build
```

Services:
- web: Django + Gunicorn on :8000
- worker: Celery worker
- zap: OWASP ZAP daemon on :8080 (internal)
- redis: broker/result

Configure with environment variables or edit `docker-compose.yml`.

## API (for Laravel or other frontends)

Set an API key (recommended):
```powershell
$env:VAPT_API_KEY = "your-strong-key"
```

Use header `X-API-Key: your-strong-key` on requests.

Endpoints:
- POST `/api/scans/create/`
  - Body JSON: `{ "target_url": "https://example.com", "engine": "zap|nmap|sqlmap|wapiti", "options": { ... } }`
  - Returns: `{ id, status }`
- GET `/api/scans/` → list recent scans
- GET `/api/scans/{id}/` → details and report_json

Example (PowerShell):
```powershell
$apiKey = "your-strong-key"
$body = @{ target_url = "https://example.com"; engine = "zap" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/scans/create/ -Headers @{"X-API-Key"=$apiKey} -Body $body -ContentType 'application/json'
```

Engines:
- zap: OWASP ZAP active scan (requires ZAP daemon)
- nmap: service/OS detection
- sqlmap: SQLi testing (requires sqlmap installed in PATH)
- wapiti: black-box web scanner (requires wapiti in PATH)

## Production notes
- Change `SECRET_KEY` and `VAPT_API_KEY` in your environment.
- Put a reverse proxy (nginx/Traefik) in front if exposing to internet.
- ZAP API key is disabled in compose for simplicity. For production use, enable key and propagate it.


