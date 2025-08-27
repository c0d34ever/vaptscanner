#!/usr/bin/env python3
"""
Test script to check ZAP connectivity and help debug connection issues
"""

import socket
import requests
import time
import sys

def test_socket_connection(host, port, service_name):
    """Test basic socket connection"""
    print(f"🔍 Testing socket connection to {service_name} ({host}:{port})...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"✅ Socket connection to {service_name} successful")
            return True
        else:
            print(f"❌ Socket connection to {service_name} failed (error code: {result})")
            return False
    except Exception as e:
        print(f"❌ Socket connection to {service_name} failed: {e}")
        return False

def test_http_connection(host, port, service_name):
    """Test HTTP connection"""
    print(f"🔍 Testing HTTP connection to {service_name}...")
    try:
        url = f"http://{host}:{port}"
        response = requests.get(url, timeout=10)
        print(f"✅ HTTP connection to {service_name} successful (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ HTTP connection to {service_name} failed: Connection refused")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ HTTP connection to {service_name} failed: Timeout")
        return False
    except Exception as e:
        print(f"❌ HTTP connection to {service_name} failed: {e}")
        return False

def test_zap_api(host, port):
    """Test ZAP API specifically"""
    print(f"🔍 Testing ZAP API at {host}:{port}...")
    try:
        # Test ZAP version endpoint
        url = f"http://{host}:{port}/JSON/core/view/version"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ ZAP API is responding (Status: {response.status_code})")
            try:
                data = response.json()
                print(f"✅ ZAP Version: {data.get('version', 'Unknown')}")
                return True
            except:
                print(f"⚠️  ZAP responded but not with JSON")
                return True
        else:
            print(f"❌ ZAP API responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ZAP API test failed: {e}")
        return False

def main():
    print("🔍 ZAP Connectivity Test Script")
    print("=" * 40)
    
    # Test different host configurations
    hosts_to_test = [
        ("zap", 8080, "ZAP (container name)"),
        ("localhost", 8090, "ZAP (localhost)"),
        ("127.0.0.1", 8090, "ZAP (127.0.0.1)"),
        ("0.0.0.0", 8090, "ZAP (0.0.0.0)"),
    ]
    
    print("\n📊 Testing different connection methods:")
    print("-" * 40)
    
    for host, port, description in hosts_to_test:
        print(f"\n🔍 Testing: {description}")
        print(f"   Host: {host}, Port: {port}")
        
        # Test socket connection
        socket_ok = test_socket_connection(host, port, description)
        
        if socket_ok:
            # Test HTTP connection
            http_ok = test_http_connection(host, port, description)
            
            if http_ok and "ZAP" in description:
                # Test ZAP API specifically
                zap_ok = test_zap_api(host, port)
                if zap_ok:
                    print(f"🎉 {description} is fully accessible!")
                    return True
        
        print(f"   {'✅' if socket_ok else '❌'} {description} connectivity")
    
    print("\n❌ All connection attempts failed")
    print("\n🔧 Troubleshooting suggestions:")
    print("1. Check if ZAP container is running: docker-compose ps zap")
    print("2. Check ZAP logs: docker-compose logs zap")
    print("3. Check if port 8090 is accessible from host")
    print("4. Try restarting ZAP: docker-compose restart zap")
    print("5. Check firewall settings on the host")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
