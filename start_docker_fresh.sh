#!/bin/bash

echo "🚀 Starting VAPT Scanner with Docker Compose (Fresh Start)..."

# Check if .env file exists, if not create from env.docker
if [ ! -f .env ]; then
    echo "📝 Creating .env file from env.docker..."
    cp env.docker .env
fi

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed or not in PATH"
    exit 1
fi

# Force stop and remove all containers
echo "🧹 Force cleaning up all containers..."
docker-compose down --remove-orphans --volumes --timeout 0

# Remove any dangling containers
echo "🗑️  Removing any dangling containers..."
docker container prune -f

# Build and start all services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 20

# Check service status
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "🎉 VAPT Scanner is starting up!"
echo ""
echo "📱 Dashboard: http://localhost:8001"
echo "🌐 Nginx Proxy: http://localhost:8080"
echo "📚 API Docs: http://localhost:8001/docs"
echo "🔍 ZAP Scanner: http://localhost:8090"
echo "🔑 API Key: vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3"
echo ""
echo "📋 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo ""
echo "⏳ Services are starting up. Please wait a few minutes for full initialization."
echo ""
echo "💡 If you see any errors, check logs with: docker-compose logs -f [service_name]"
echo "💡 Port configuration: FastAPI(8001), Nginx(8080), ZAP(8090), Redis(6379)"
