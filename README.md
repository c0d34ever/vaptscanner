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

### .env support
- Create a `.env` file in project root (same folder as `manage.py`).
- Recognized keys (see `ENV_EXAMPLE.txt`):
  - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
  - `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
  - `ZAP_HTTP`, `ZAP_HTTPS`, `VAPT_API_KEY`
  - Optional for dev without Redis: `CELERY_ALWAYS_EAGER=true`, `CELERY_EAGER_PROPAGATES=true`

Auto-start a scan on deploy
- Set envs before `docker compose up` (or in your VPS environment):
```bash
export STARTUP_SCAN_URL="https://example.com"
export STARTUP_SCAN_ENGINE="zap"   # or nmap|sqlmap|wapiti
```
The web container will enqueue a scan at startup.

## API (for Laravel or other frontends)

Set an API key (recommended):
```powershell
$env:VAPT_API_KEY = "your-strong-key"
```

Use header `X-API-Key: your-strong-key` on requests.

### Core Endpoints
- POST `/api/scans/create/`
  - Body JSON: `{ "target_url": "https://example.com", "engine": "zap|nmap|sqlmap|wapiti", "options": { ... } }`
  - Returns: `{ id, status }`
- GET `/api/scans/` → list recent scans
- GET `/api/scans/{id}/` → details and report_json
- GET `/api/scans/{id}/logs/` → structured scan logs

### Enhanced Features
- **Templates**: 
  - POST `/api/templates/create/` → create scan template
  - GET `/api/templates/` → list available templates
- **Scheduling**: 
  - POST `/api/scheduled/create/` → create recurring scan
  - GET `/api/scheduled/` → list scheduled scans
- **Bulk Operations**: 
  - POST `/api/bulk-scan/` → scan multiple URLs at once
- **Analytics**: 
  - GET `/api/stats/` → scan statistics and charts
- **Export**: 
  - GET `/api/scans/{id}/export/?format=csv|json` → download results
- **Search**: 
  - GET `/api/search/?q=query&engine=zap&status=completed` → advanced filtering

### Example (PowerShell):
```powershell
$apiKey = "your-strong-key"
$body = @{ target_url = "https://example.com"; engine = "zap" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/scans/create/ -Headers @{"X-API-Key"=$apiKey} -Body $body -ContentType 'application/json'
```

## Test frontend (Playground)
- Open `/playground/` in your browser to try the API quickly.
- Enter Base URL, API Key, target, and engine, then click Create Scan or List Scans.

## Engines
- zap: OWASP ZAP active scan (requires ZAP daemon)
- nmap: service/OS detection
- sqlmap: SQLi testing (requires sqlmap installed in PATH)
- wapiti: black-box web scanner (requires wapiti in PATH)

## Features Overview

### 🎯 **Core Scanning**
- Multi-engine support (ZAP, Nmap, SQLMap, Wapiti)
- Real-time scan progress tracking
- Structured logging and error reporting
- Comprehensive vulnerability findings

### 📊 **Dashboard & Analytics**
- Interactive charts (Chart.js)
- Real-time statistics
- Scan status distribution
- Engine usage analytics
- Search and filtering

### 🚀 **Advanced Operations**
- **Scan Templates**: Predefined configurations for consistent scanning
- **Bulk Scanning**: Scan multiple targets simultaneously
- **Scheduled Scans**: Automated recurring scans (daily/weekly/monthly)
- **Export Options**: CSV, JSON formats for reports
- **Advanced Search**: Filter by engine, status, severity, keywords

### 🔧 **Management Features**
- Priority-based scan queuing
- Tag-based organization
- Notes and annotations
- False positive marking
- CVE tracking and CVSS scoring
- Remediation guidance

### 📈 **Monitoring & Reporting**
- Detailed scan logs with timestamps
- Performance metrics and duration tracking
- Critical findings alerts
- Historical trend analysis
- Comparison between scans

## Production notes
- Change `SECRET_KEY` and `VAPT_API_KEY` in your environment.
- Put a reverse proxy (nginx/Traefik) in front if exposing to internet.
- ZAP API key is disabled in compose for simplicity. For production use, enable key and propagate it.
- Run migrations after deployment: `python manage.py migrate`
- Monitor scan logs via `/api/scans/{id}/logs/` endpoint
- Use templates for consistent scan configurations across teams


