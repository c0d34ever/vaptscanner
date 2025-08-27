#!/bin/bash

echo "🚀 Starting VAPT Scanner without ZAP dependency (for testing)..."

# Check if .env file exists, if not create from env.docker
if [ ! -f .env ]; then
    echo "📝 Creating .env file from env.docker..."
    cp env.docker .env
fi

# Stop all services
echo "🛑 Stopping all services..."
docker-compose down

# Start services without ZAP
echo "🔨 Starting services (excluding ZAP)..."
docker-compose up -d redis fastapi worker nginx

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service status
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "🎉 VAPT Scanner is starting up (without ZAP)!"
echo ""
echo "📱 Dashboard: http://YOUR_SERVER_IP:8001"
echo "🌐 Nginx Proxy: http://YOUR_SERVER_IP:8080"
echo "📚 API Docs: http://YOUR_SERVER_IP:8001/docs"
echo "🔑 API Key: vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3"
echo ""
echo "⚠️  Note: ZAP is not running, so ZAP-based scans will not work"
echo "💡 To start with ZAP later: docker-compose up -d zap"
echo ""
echo "📋 To view logs: docker-compose logs -f fastapi"
echo "🛑 To stop: docker-compose down"
