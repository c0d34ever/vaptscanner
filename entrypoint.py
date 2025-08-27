#!/usr/bin/env python3
"""
Entrypoint script for VAPT Scanner FastAPI Application
This script handles startup tasks and then starts the FastAPI server
"""

import os
import time
import subprocess
import socket
import sys
from pathlib import Path

def wait_for_service(host, port, service_name, max_wait=60):
    """Wait for a service to be ready"""
    print(f"⏳ Waiting for {service_name}...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                print(f"✅ {service_name} is ready")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"❌ {service_name} failed to start within {max_wait} seconds")
    return False

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Starting VAPT Scanner FastAPI Application...")
    
    # Wait for Redis
    if not wait_for_service("redis", 6379, "Redis"):
        print("❌ Redis is not available, exiting")
        sys.exit(1)
    
    # Wait for ZAP
    if not wait_for_service("zap", 8080, "ZAP"):
        print("❌ ZAP is not available, exiting")
        sys.exit(1)
    
    # Apply Django migrations
    if not run_command("python manage.py migrate", "Applying Django migrations"):
        print("⚠️ Migrations failed, but continuing...")
    
    # Create superuser if it doesn't exist
    superuser_cmd = '''
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
'''
    if not run_command(superuser_cmd, "Checking for superuser"):
        print("⚠️ Superuser creation failed, but continuing...")
    
    # Run startup scan if configured
    startup_url = os.environ.get('STARTUP_SCAN_URL')
    startup_engine = os.environ.get('STARTUP_SCAN_ENGINE')
    
    if startup_url and startup_engine:
        print(f"🚀 Running startup scan on {startup_url} with {startup_engine}...")
        if not run_command("python manage.py startup_scan", "Startup scan"):
            print("⚠️ Startup scan failed, but continuing...")
    
    # Start FastAPI application
    print("🚀 Starting FastAPI server...")
    os.execvp("python", ["python", "fastapi_app.py"])

if __name__ == "__main__":
    main()
