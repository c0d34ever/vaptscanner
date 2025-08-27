# VAPT Scanner - FastAPI Version with Modern UI

A comprehensive, self-hosted Vulnerability Assessment and Penetration Testing (VAPT) solution built with FastAPI and a modern web interface.

## 🚀 Features

### Core Functionality
- **Multi-Engine Scanning**: OWASP ZAP (DAST), Nmap (Network), SQLMap (SQL Injection), Wapiti (Web Vulnerabilities)
- **Real-time Dashboard**: Interactive charts, statistics, and real-time scan monitoring
- **Modern Web UI**: Responsive Bootstrap-based interface with Chart.js visualizations
- **RESTful API**: JSON-based API with comprehensive authentication
- **Scan Management**: Create, monitor, and manage scans with detailed logging
- **Template System**: Predefined scan configurations for consistency
- **Scheduled Scans**: Automated scanning with configurable frequencies
- **Bulk Operations**: Scan multiple targets simultaneously
- **Export & Reporting**: Multiple format support (JSON, CSV)
- **Search & Filtering**: Advanced search capabilities across scans and findings

### Technical Features
- **FastAPI Backend**: High-performance, async-capable API framework
- **Django ORM**: Robust database management and migrations
- **Celery Integration**: Asynchronous task processing for long-running scans
- **Environment Configuration**: Flexible configuration via environment variables
- **CORS Support**: Configurable cross-origin resource sharing
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Structured Logging**: Detailed scan execution logs for debugging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser  │    │   FastAPI App   │    │   Django ORM    │
│   (Dashboard)  │◄──►│   (API Layer)   │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Celery Tasks  │
                       │  (Scan Engine)  │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Scan Engines   │
                       │ ZAP, Nmap, etc. │
                       └─────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vapt-scan-api
   ```

2. **Run the startup script**
   ```bash
   python start_fastapi.py
   ```

   This script will:
   - Create a `.env` file from `env_example.txt`
   - Install required dependencies
   - Set up the Django database
   - Start the FastAPI server

3. **Access the application**
   - **Dashboard**: http://localhost:8001
   - **API Docs**: http://localhost:8001/docs
   - **Health Check**: http://localhost:8001/health

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements_fastapi.txt
   ```

2. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

3. **Initialize Django**
   ```bash
   python startup_fastapi.py
   ```

4. **Start the server**
   ```bash
   python fastapi_app.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=true
ALLOWED_HOSTS=*

# VAPT API Settings
VAPT_API_KEY=your-api-key-here

# Celery Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_ALWAYS_EAGER=true
CELERY_EAGER_PROPAGATES=false

# ZAP Settings
ZAP_HTTP=http://127.0.0.1:8080
ZAP_HTTPS=http://127.0.0.1:8080

# CORS Settings
CORS_ALLOW_ALL=true
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:8001

# FastAPI Settings
API_HOST=0.0.0.0
API_PORT=8001
```

### API Key Authentication

All API endpoints require authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8001/api/scans/
```

## 📱 Web Interface

### Dashboard Features

- **Statistics Cards**: Total scans, completed scans, in-progress scans, critical findings
- **Interactive Charts**: Scan activity over time, engine distribution
- **Recent Scans Table**: Quick overview of latest scan results
- **Quick Actions**: Start new scans, refresh data, navigate sections

### Navigation Sections

1. **Dashboard**: Overview and statistics
2. **Scans**: All scans with search and filtering
3. **Templates**: Predefined scan configurations
4. **Scheduled**: Automated scan scheduling
5. **Bulk Scans**: Multiple target scanning
6. **Reports**: Detailed scan reports and exports

### Responsive Design

- Mobile-friendly interface
- Bootstrap 5 components
- Font Awesome icons
- Chart.js visualizations
- Modern color scheme and gradients

## 🔌 API Endpoints

### Authentication
All endpoints require the `X-API-Key` header with your API key.

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard UI |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

### Scan Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scans/create/` | POST | Create new scan |
| `/api/scans/` | GET | List all scans |
| `/api/scans/{id}/` | GET | Get scan details |
| `/api/scans/{id}/logs/` | GET | Get scan logs |
| `/api/scans/{id}/export/` | GET | Export scan results |

### Templates

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/templates/create/` | POST | Create scan template |
| `/api/templates/` | GET | List all templates |

### Scheduling

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scheduled/create/` | POST | Create scheduled scan |
| `/api/scheduled/` | GET | List scheduled scans |

### Bulk Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bulk-scan/` | POST | Create multiple scans |

### Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats/` | GET | Get scan statistics |
| `/api/search/` | GET | Search scans with filters |

## 🔍 Usage Examples

### Start a New Scan

```bash
curl -X POST "http://localhost:8001/api/scans/create/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "target_url": "https://example.com",
    "engine": "zap",
    "options": {"depth": 3, "threads": 10}
  }'
```

### Get Scan Statistics

```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8001/api/stats/?days=30"
```

### Search Scans

```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8001/api/search/?q=example.com&engine=zap"
```

### Export Scan Results

```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8001/api/scans/1/export/?format=json"
```

## 🐳 Docker Deployment

### Using Docker Compose

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     fastapi:
       build: .
       ports:
         - "8001:8001"
       environment:
         - VAPT_API_KEY=your-api-key
       volumes:
         - .:/app
       depends_on:
         - redis
         - zap
     
     worker:
       build: .
       command: celery -A vapt_platform worker --loglevel=info
       environment:
         - VAPT_API_KEY=your-api-key
       volumes:
         - .:/app
       depends_on:
         - redis
         - zap
     
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
     
     zap:
       image: ghcr.io/zaproxy/zaproxy:stable
       ports:
         - "8080:8080"
   ```

2. **Build and run**
   ```bash
   docker-compose up -d --build
   ```

## 🔧 Development

### Project Structure

```
vapt-scan-api/
├── fastapi_app.py          # Main FastAPI application
├── env_config.py           # Environment configuration
├── start_fastapi.py        # Startup script
├── static/                 # Static files (UI)
│   ├── index.html         # Main dashboard
│   └── js/
│       └── app.js         # Frontend JavaScript
├── scans/                  # Django app with models and tasks
├── vapt_platform/          # Django project settings
├── requirements_fastapi.txt # FastAPI dependencies
└── env_example.txt         # Environment template
```

### Running in Development Mode

1. **Set DEBUG=true in .env**
2. **Start the server**
   ```bash
   python fastapi_app.py
   ```
3. **Access development endpoints**
   - http://localhost:8001/docs (Interactive API docs)
   - http://localhost:8001/redoc (ReDoc documentation)

### API Development

- **Add new endpoints**: Edit `fastapi_app.py`
- **Update models**: Edit `scans/models.py`
- **Add tasks**: Edit `scans/tasks.py`
- **Frontend changes**: Edit `static/js/app.js`

## 🚨 Security Considerations

- **API Key Protection**: Keep your API key secure and rotate regularly
- **Network Security**: Restrict access to the API server
- **CORS Configuration**: Configure allowed origins for production
- **Input Validation**: All inputs are validated via Pydantic models
- **Authentication**: All endpoints require valid API key

## 📊 Monitoring and Logging

### Logs
- **Scan Logs**: Detailed execution logs for each scan
- **API Logs**: FastAPI access and error logs
- **Task Logs**: Celery worker execution logs

### Health Checks
- **Endpoint**: `/health`
- **Database connectivity**
- **External service status**
- **API version information**

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in .env
   API_PORT=8002
   ```

2. **Database errors**
   ```bash
   # Reinitialize Django
   python startup_fastapi.py
   ```

3. **CORS issues**
   ```bash
   # Update CORS settings in .env
   CORS_ALLOW_ALL=true
   ```

4. **API key authentication fails**
   ```bash
   # Check VAPT_API_KEY in .env
   # Ensure X-API-Key header is set
   ```

### Getting Help

- Check the logs for detailed error messages
- Verify environment variable configuration
- Ensure all dependencies are installed
- Check API documentation at `/docs`

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
pip install -r requirements_fastapi.txt --upgrade
```

### Database Migrations
```bash
python manage.py migrate
```

### Backup and Restore
```bash
# Backup
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3

# Restore
cp backup_file.sqlite3 db.sqlite3
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the documentation at `/docs`
- Review the troubleshooting section
- Open an issue on GitHub

---

**Happy Scanning! 🚀🔍**
