#!/usr/bin/env python3
"""
FastAPI VAPT Scanner Startup Script
Initializes database and starts the FastAPI server
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Initialize Django for model access"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vapt_platform.settings')
    django.setup()

def run_migrations():
    """Run Django migrations"""
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])

def create_superuser():
    """Create superuser if none exists"""
    from django.contrib.auth.models import User
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser created: admin/admin123")

def startup_scan():
    """Run startup scan if configured"""
    from django.conf import settings
    from scans.models import Scan
    from scans.tasks import run_vapt_scan
    
    startup_url = getattr(settings, 'STARTUP_SCAN_URL', None)
    startup_engine = getattr(settings, 'STARTUP_SCAN_ENGINE', 'zap')
    
    if startup_url:
        print(f"Creating startup scan for {startup_url} with {startup_engine}...")
        scan = Scan.objects.create(
            target_url=startup_url,
            engine=startup_engine
        )
        run_vapt_scan.delay(scan.id)
        print(f"Startup scan {scan.id} created and queued")

def main():
    """Main startup function"""
    print("Starting VAPT Scanner FastAPI...")
    
    try:
        # Setup Django
        setup_django()
        print("✓ Django initialized")
        
        # Run migrations
        run_migrations()
        print("✓ Database migrations completed")
        
        # Create superuser if needed
        create_superuser()
        print("✓ User setup completed")
        
        # Startup scan if configured
        startup_scan()
        print("✓ Startup scan configured")
        
        print("\n🎉 FastAPI VAPT Scanner is ready!")
        print("📚 API Documentation: http://localhost:8001/docs")
        print("🔍 ReDoc Documentation: http://localhost:8001/redoc")
        print("🏥 Health Check: http://localhost:8001/health")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
