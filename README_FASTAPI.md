# VAPT Scanner - FastAPI Version 🚀

A high-performance, modern API for Vulnerability Assessment and Penetration Testing built with **FastAPI** and **Django ORM**.

## ✨ **Why FastAPI?**

- **🚀 Performance**: 2-3x faster than Django REST Framework
- **📚 Auto-documentation**: Interactive Swagger/OpenAPI docs
- **🔒 Type Safety**: Full Pydantic validation and type hints
- **⚡ Async Support**: Native async/await for better concurrency
- **🔄 Modern**: Built for modern Python (3.7+) with latest standards

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │   Django ORM    │    │   Celery Tasks  │
│   (Port 8001)   │◄──►│   (Models)      │◄──►│   (Scans)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Redis Broker  │    │   ZAP Scanner   │
│   (Port 80/443) │    │   (Port 6379)   │    │   (Port 8080)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Option 1: Docker Compose (Recommended)**

```bash
# Clone and setup
git clone <your-repo>
cd vapt-scan-api

# Set environment variables
export VAPT_API_KEY="your-super-secure-key"
export SECRET_KEY="your-django-secret-key"

# Start all services
docker compose -f docker-compose.fastapi.yml up -d --build

# Check status
docker compose -f docker-compose.fastapi.yml ps
```

### **Option 2: Local Development**

```bash
# Install dependencies
pip install -r requirements_fastapi.txt
pip install -r requirements.txt

# Setup database
python startup_fastapi.py

# Start FastAPI server
python fastapi_app.py
```

## 🌐 **API Endpoints**

### **Core Scanning**
- `POST /api/scans/create/` - Create new scan
- `GET /api/scans/` - List all scans
- `GET /api/scans/{id}/` - Get scan details
- `GET /api/scans/{id}/logs/` - Get scan logs

### **Templates & Scheduling**
- `POST /api/templates/create/` - Create scan template
- `GET /api/templates/` - List templates
- `POST /api/scheduled/create/` - Schedule recurring scan
- `GET /api/scheduled/` - List scheduled scans

### **Advanced Features**
- `POST /api/bulk-scan/` - Scan multiple targets
- `GET /api/stats/` - Analytics and statistics
- `GET /api/scans/{id}/export/` - Export results (CSV/JSON)
- `GET /api/search/` - Advanced search with filters

### **Utility**
- `GET /health` - Health check
- `GET /api/test/` - Test API key authentication

## 📚 **Interactive Documentation**

Once running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## 🔑 **Authentication**

All API endpoints require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-super-secure-key" \
     http://localhost:8001/api/scans/
```

## 📊 **Example Usage**

### **Create a Scan**
```bash
curl -X POST "http://localhost:8001/api/scans/create/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-super-secure-key" \
  -d '{
    "target_url": "https://example.com",
    "engine": "zap",
    "options": {"depth": 3}
  }'
```

### **Bulk Scan**
```bash
curl -X POST "http://localhost:8001/api/bulk-scan/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-super-secure-key" \
  -d '{
    "urls": [
      "https://site1.com",
      "https://site2.com",
      "https://site3.com"
    ],
    "engine": "nmap"
  }'
```

### **Get Statistics**
```bash
curl -H "X-API-Key: your-super-secure-key" \
     "http://localhost:8001/api/stats/?days=7"
```

## 🐳 **Docker Services**

| Service | Port | Purpose |
|---------|------|---------|
| `fastapi` | 8001 | Main API server |
| `worker` | - | Celery background tasks |
| `redis` | 6379 | Message broker |
| `zap` | 8080 | OWASP ZAP scanner |
| `nginx` | 80/443 | Reverse proxy |

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Required
VAPT_API_KEY=your-super-secure-key
SECRET_KEY=your-django-secret-key

# Optional
DEBUG=False
ALLOWED_HOSTS=*
DATABASE_URL=sqlite:///db.sqlite3
CELERY_BROKER_URL=redis://redis:6379/0
ZAP_HTTP=http://zap:8080
STARTUP_SCAN_URL=https://example.com
STARTUP_SCAN_ENGINE=zap
```

### **Database**

The FastAPI version uses Django ORM for database access, so you get:
- **SQLite** (default) - Good for development
- **PostgreSQL** - Production ready
- **MySQL** - Enterprise support

## 📈 **Performance Benefits**

- **Response Time**: 2-3x faster than Django REST
- **Concurrent Requests**: Better async handling
- **Memory Usage**: More efficient request processing
- **Documentation**: Auto-generated, always up-to-date

## 🔍 **Monitoring & Debugging**

### **Health Check**
```bash
curl http://localhost:8001/health
```

### **Container Logs**
```bash
# FastAPI logs
docker compose -f docker-compose.fastapi.yml logs fastapi

# Worker logs
docker compose -f docker-compose.fastapi.yml logs worker

# ZAP logs
docker compose -f docker-compose.fastapi.yml logs zap
```

### **Database Access**
```bash
# Django shell
docker compose -f docker-compose.fastapi.yml exec fastapi python manage.py shell

# Check scan status
docker compose -f docker-compose.fastapi.yml exec fastapi python -c "
from scans.models import Scan
print('Total scans:', Scan.objects.count())
print('Recent scans:', [(s.id, s.status) for s in Scan.objects.all()[:5]])
"
```

## 🚀 **Production Deployment**

### **1. Set Production Environment**
```bash
export VAPT_API_KEY="production-secure-key"
export SECRET_KEY="production-django-key"
export DEBUG=False
export ALLOWED_HOSTS=your-domain.com
```

### **2. Start Services**
```bash
docker compose -f docker-compose.fastapi.yml up -d --build
```

### **3. Configure Nginx (Optional)**
The compose file includes Nginx for SSL termination and load balancing.

### **4. Monitor**
```bash
# Check all services
docker compose -f docker-compose.fastapi.yml ps

# View logs
docker compose -f docker-compose.fastapi.yml logs -f
```

## 🔄 **Migration from Django**

If you're currently using the Django version:

1. **Keep Django models** - FastAPI uses Django ORM
2. **Update API calls** - Use new FastAPI endpoints
3. **Same database** - No data migration needed
4. **Better performance** - 2-3x faster responses

## 🆚 **Django vs FastAPI Comparison**

| Feature | Django | FastAPI |
|---------|--------|---------|
| **Performance** | Good | Excellent (2-3x faster) |
| **Documentation** | Manual | Auto-generated |
| **Type Safety** | Basic | Full Pydantic |
| **Async Support** | Limited | Native |
| **Learning Curve** | Moderate | Easy |
| **Ecosystem** | Mature | Growing |

## 🎯 **Use Cases**

- **High-traffic APIs** - Better performance under load
- **Microservices** - Lightweight, focused services
- **Real-time scanning** - Better async handling
- **Modern frontends** - Perfect for React/Vue/Angular
- **Enterprise integration** - Professional API documentation

## 🆘 **Troubleshooting**

### **Common Issues**

1. **Port conflicts**: Change ports in docker-compose.fastapi.yml
2. **Database errors**: Run `python startup_fastapi.py`
3. **ZAP connection**: Check ZAP container logs
4. **API key errors**: Verify VAPT_API_KEY environment variable

### **Debug Mode**
```bash
export DEBUG=True
docker compose -f docker-compose.fastapi.yml up --build
```

## 📞 **Support**

- **Issues**: Check container logs
- **API Docs**: Visit `/docs` endpoint
- **Health**: Use `/health` endpoint
- **Database**: Use Django management commands

---

**🎉 FastAPI VAPT Scanner - Modern, Fast, Secure!**
