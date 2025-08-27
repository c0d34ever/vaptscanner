#!/bin/bash

echo "🚀 Starting VAPT Scanner with Docker Compose (Clean Version)..."

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

# Clean up any existing containers and orphaned containers
echo "🧹 Cleaning up existing containers..."
docker-compose down --remove-orphans

# Build and start all services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service status
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "🎉 VAPT Scanner is starting up!"
echo ""
echo "📱 Dashboard: http://localhost:8001"
echo "🌐 Nginx Proxy: http://localhost:8080"
echo "📚 API Docs: http://localhost:8001/docs"
echo "🔑 API Key: vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3"
echo ""
echo "📋 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo ""
echo "⏳ Services are starting up. Please wait a few minutes for full initialization."
echo ""
echo "💡 If you see any permission errors, the Python entrypoint script should handle them automatically."
