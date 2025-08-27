#!/usr/bin/env python3
"""
Startup script for VAPT Scanner FastAPI application
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting VAPT Scanner FastAPI Application...")
    
    # Check if we're in the right directory
    if not Path("fastapi_app.py").exists():
        print("❌ Error: fastapi_app.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if .env exists, if not create from example
    if not Path(".env").exists():
        if Path("env_example.txt").exists():
            print("📝 Creating .env file from env_example.txt...")
            try:
                with open("env_example.txt", "r") as src, open(".env", "w") as dst:
                    dst.write(src.read())
                print("✅ .env file created successfully")
            except Exception as e:
                print(f"❌ Failed to create .env file: {e}")
                sys.exit(1)
        else:
            print("⚠️  Warning: No .env file found and no env_example.txt available")
    
    # Check if Django is set up
    if not Path("db.sqlite3").exists():
        print("🔧 Setting up Django database...")
        try:
            # Run Django setup
            subprocess.run([sys.executable, "startup_fastapi.py"], check=True)
            print("✅ Django setup completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Django setup failed: {e}")
            sys.exit(1)
    
    # Install FastAPI dependencies if needed
    print("📦 Checking FastAPI dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_fastapi.txt"], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)
    
    # Start FastAPI application
    print("🚀 Starting FastAPI server...")
    print("📱 Dashboard will be available at: http://localhost:8001")
    print("📚 API docs will be available at: http://localhost:8001/docs")
    print("🔑 API Key: vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        subprocess.run([sys.executable, "fastapi_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
