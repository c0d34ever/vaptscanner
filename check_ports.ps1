# PowerShell script to check port availability for VAPT Scanner

Write-Host "🔍 Checking Port Availability for VAPT Scanner..." -ForegroundColor Green
Write-Host ""

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        return $connection.TcpTestSucceeded
    } catch {
        return $false
    }
}

# Function to find next available port
function Find-AvailablePort {
    param([int]$StartPort)
    $port = $StartPort
    while (Test-Port -Port $port) {
        $port++
    }
    return $port
}

# Check required ports
$ports = @(
    @{Port=8001; Service="FastAPI Dashboard"},
    @{Port=8080; Service="Nginx Proxy"},
    @{Port=8443; Service="Nginx HTTPS"},
    @{Port=6379; Service="Redis"},
    @{Port=8080; Service="ZAP Scanner"}
)

Write-Host "📊 Port Status Check:" -ForegroundColor Yellow
Write-Host ""

$conflicts = @()
foreach ($portInfo in $ports) {
    $port = $portInfo.Port
    $service = $portInfo.Service
    
    if (Test-Port -Port $port) {
        Write-Host "❌ Port $port ($service): IN USE" -ForegroundColor Red
        $conflicts += @{Port=$port; Service=$service}
    } else {
        Write-Host "✅ Port $port ($service): AVAILABLE" -ForegroundColor Green
    }
}

Write-Host ""

if ($conflicts.Count -gt 0) {
    Write-Host "⚠️  Port Conflicts Detected!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Suggested Solutions:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($conflict in $conflicts) {
        $port = $conflict.Port
        $service = $conflict.Service
        $suggestedPort = Find-AvailablePort -StartPort ($port + 1)
        
        Write-Host "   $service (Port $port) → Use Port $suggestedPort instead" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "💡 To fix port conflicts:" -ForegroundColor Green
    Write-Host "   1. Copy docker-compose.override.yml.example to docker-compose.override.yml" -ForegroundColor White
    Write-Host "   2. Modify the ports in the override file" -ForegroundColor White
    Write-Host "   3. Run: docker-compose up -d --build" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Example override file:" -ForegroundColor Yellow
    Write-Host "   services:" -ForegroundColor White
    Write-Host "     nginx:" -ForegroundColor White
    Write-Host "       ports:" -ForegroundColor White
    Write-Host "         - '9000:80'    # Use port 9000 instead of 8080" -ForegroundColor White
    Write-Host "         - '9443:443'   # Use port 9443 instead of 8443" -ForegroundColor White
} else {
    Write-Host "🎉 All ports are available! You can start the VAPT Scanner." -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Run: .\start_docker_clean.ps1" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📚 For more information, see README_DOCKER.md" -ForegroundColor Gray
