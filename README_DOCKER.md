# VAPT Scanner - Docker Deployment Guide

This guide covers deploying the VAPT Scanner using Docker and Docker Compose with all necessary services.

## 🐳 Services Overview

The Docker setup includes the following services:

| Service | Port | Description |
|---------|------|-------------|
| **FastAPI** | 8001 | Main application server with UI |
| **Worker** | - | Celery worker for background tasks |
| **Redis** | 6379 | Message broker and result backend |
| **ZAP** | 8080 | OWASP ZAP security scanner |
| **Nginx** | 80 | Reverse proxy and load balancer |

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd vapt-scan-api
```

### 2. Start All Services

**On Linux/macOS:**
```bash
chmod +x start_docker.sh
./start_docker.sh
```

**On Windows (PowerShell):**
```powershell
.\start_docker.ps1
```

**Manual Start:**
```bash
docker-compose up -d --build
```

### 3. Access the Application
- **Dashboard**: http://localhost:8001
- **Nginx Proxy**: http://localhost
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🔧 Configuration

### Environment Variables
The application uses environment variables for configuration. A production-ready configuration is provided in `env.docker`.

Key variables:
```bash
VAPT_API_KEY=vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3
SECRET_KEY=django-secret-1aZ3Qm9YpQ6uZr0F8dV7xK2wB5eN4tH9sJ3uC1pL7qT0mR6yV2aW
DEBUG=False
CELERY_BROKER_URL=redis://redis:6379/0
ZAP_HTTP=http://zap:8080
```

### Custom Configuration
1. Copy `env.docker` to `.env`
2. Edit `.env` with your settings
3. Restart services: `docker-compose restart`

## 📊 Service Management

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f worker
docker-compose logs -f redis
docker-compose logs -f zap
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Update and Rebuild
```bash
docker-compose down
docker-compose up -d --build
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8001

# Stop conflicting service or change port in docker-compose.yml
```

#### 2. Permission Issues
```bash
# On Linux, ensure your user is in the docker group
sudo usermod -aG docker $USER
# Log out and back in
```

#### 3. Service Not Starting
```bash
# Check logs for errors
docker-compose logs fastapi

# Check service status
docker-compose ps
```

#### 4. Database Issues
```bash
# Reset database (WARNING: This will delete all data)
docker-compose down
rm -f db.sqlite3
docker-compose up -d --build
```

### Health Checks

#### FastAPI Health
```bash
curl http://localhost:8001/health
```

#### Redis Health
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

#### ZAP Health
```bash
curl http://localhost:8080/JSON/core/view/version
```

## 🏗️ Architecture Details

### Service Dependencies
```
Nginx → FastAPI → Django ORM → SQLite
    ↓
Worker → Celery → Redis
    ↓
ZAP Scanner
```

### Data Persistence
- **Database**: SQLite file mounted as volume
- **Media**: Uploaded files stored in media directory
- **Logs**: Container logs accessible via docker-compose logs

### Network Configuration
- **Internal**: Services communicate via Docker network
- **External**: FastAPI exposed on port 8001, Nginx on port 80
- **ZAP**: Accessible on port 8080 for debugging

## 🔒 Security Considerations

### Production Deployment
1. **Change default API keys** in `.env`
2. **Use HTTPS** with proper SSL certificates
3. **Restrict network access** to necessary ports only
4. **Regular updates** of base images
5. **Monitor logs** for suspicious activity

### API Key Management
- Rotate API keys regularly
- Use strong, unique keys
- Restrict access by IP if possible
- Monitor API usage

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale worker services
docker-compose up -d --scale worker=3

# Scale FastAPI services (requires load balancer)
docker-compose up -d --scale fastapi=2
```

### Resource Limits
Add resource constraints in `docker-compose.yml`:
```yaml
services:
  fastapi:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Database Migrations
```bash
# Run migrations
docker-compose exec fastapi python manage.py migrate

# Create superuser
docker-compose exec fastapi python manage.py createsuperuser
```

### Backup and Restore
```bash
# Backup database
docker-compose exec fastapi cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3

# Restore database
docker-compose exec fastapi cp backup_file.sqlite3 db.sqlite3
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)

### Support
- Check logs: `docker-compose logs -f`
- API documentation: http://localhost:8001/docs
- Health endpoint: http://localhost:8001/health

---

**Happy Scanning! 🚀🔍**
