# PowerShell script to start VAPT Scanner with Docker Compose (Fresh Start)

Write-Host "🚀 Starting VAPT Scanner with Docker Compose (Fresh Start)..." -ForegroundColor Green

# Check if .env file exists, if not create from env.docker
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from env.docker..." -ForegroundColor Yellow
    Copy-Item "env.docker" ".env"
}

# Check if Docker and Docker Compose are available
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Force stop and remove all containers
Write-Host "🧹 Force cleaning up all containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans --volumes --timeout 0

# Remove any dangling containers
Write-Host "🗑️  Removing any dangling containers..." -ForegroundColor Yellow
docker container prune -f

# Build and start all services
Write-Host "🔨 Building and starting services..." -ForegroundColor Yellow
docker-compose up -d --build

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "🎉 VAPT Scanner is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Dashboard: http://localhost:8001" -ForegroundColor Cyan
Write-Host "🌐 Nginx Proxy: http://localhost:8080" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "🔍 ZAP Scanner: http://localhost:8090" -ForegroundColor Cyan
Write-Host "🔑 API Key: vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 To view logs: docker-compose logs -f" -ForegroundColor White
Write-Host "🛑 To stop: docker-compose down" -ForegroundColor White
Write-Host "🔄 To restart: docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "⏳ Services are starting up. Please wait a few minutes for full initialization." -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 If you see any errors, check logs with: docker-compose logs -f [service_name]" -ForegroundColor Green
Write-Host "💡 Port configuration: FastAPI(8001), Nginx(8080), ZAP(8090), Redis(6379)" -ForegroundColor Green
