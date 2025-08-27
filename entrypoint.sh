#!/bin/bash
set -e

echo "🚀 Starting VAPT Scanner FastAPI Application..."

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "✅ Redis is ready"

# Wait for ZAP to be ready
echo "⏳ Waiting for ZAP..."
while ! nc -z zap 8080; do
  sleep 1
done
echo "✅ ZAP is ready"

# Apply Django migrations
echo "🔧 Applying Django migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Run startup scan if configured
if [ ! -z "$STARTUP_SCAN_URL" ] && [ ! -z "$STARTUP_SCAN_ENGINE" ]; then
    echo "🚀 Running startup scan on $STARTUP_SCAN_URL with $STARTUP_SCAN_ENGINE..."
    python manage.py startup_scan
fi

# Start FastAPI application
echo "🚀 Starting FastAPI server..."
exec python fastapi_app.py
