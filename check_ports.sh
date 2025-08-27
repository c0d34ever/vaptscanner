#!/bin/bash

echo "🔍 Checking Port Availability for VAPT Scanner..."
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if command -v netstat >/dev/null 2>&1; then
        netstat -tuln | grep -q ":$port "
    elif command -v ss >/dev/null 2>&1; then
        ss -tuln | grep -q ":$port "
    elif command -v lsof >/dev/null 2>&1; then
        lsof -i :$port >/dev/null 2>&1
    else
        echo "❌ No port checking tool available (netstat, ss, or lsof)"
        return 1
    fi
}

# Function to find next available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    while check_port $port; do
        port=$((port + 1))
    done
    echo $port
}

# Check required ports
ports=(
    "8001:FastAPI Dashboard"
    "8080:Nginx Proxy"
    "8443:Nginx HTTPS"
    "6379:Redis"
    "8080:ZAP Scanner"
)

echo "📊 Port Status Check:"
echo ""

conflicts=()
for port_info in "${ports[@]}"; do
    port=$(echo $port_info | cut -d: -f1)
    service=$(echo $port_info | cut -d: -f2)
    
    if check_port $port; then
        echo "❌ Port $port ($service): IN USE"
        conflicts+=("$port:$service")
    else
        echo "✅ Port $port ($service): AVAILABLE"
    fi
done

echo ""

if [ ${#conflicts[@]} -gt 0 ]; then
    echo "⚠️  Port Conflicts Detected!"
    echo ""
    echo "🔧 Suggested Solutions:"
    echo ""
    
    for conflict in "${conflicts[@]}"; do
        port=$(echo $conflict | cut -d: -f1)
        service=$(echo $conflict | cut -d: -f2)
        suggested_port=$(find_available_port $((port + 1)))
        
        echo "   $service (Port $port) → Use Port $suggested_port instead"
    done
    
    echo ""
    echo "💡 To fix port conflicts:"
    echo "   1. Copy docker-compose.override.yml.example to docker-compose.override.yml"
    echo "   2. Modify the ports in the override file"
    echo "   3. Run: docker-compose up -d --build"
    echo ""
    echo "📋 Example override file:"
    echo "   services:"
    echo "     nginx:"
    echo "       ports:"
    echo "         - '9000:80'    # Use port 9000 instead of 8080"
    echo "         - '9443:443'   # Use port 9443 instead of 8443"
else
    echo "🎉 All ports are available! You can start the VAPT Scanner."
    echo ""
    echo "🚀 Run: ./start_docker_clean.sh"
fi

echo ""
echo "📚 For more information, see README_DOCKER.md"
