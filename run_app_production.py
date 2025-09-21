#!/usr/bin/env python3
"""
Production-ready Flask app runner using Waitress (Windows-compatible WSGI server)
"""
import os
import sys

# Install waitress if not available: pip install waitress
try:
    from waitress import serve
except ImportError:
    print("❌ Waitress not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "waitress"])
    from waitress import serve

from web_app import app

def main():
    # Set environment variables
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    print("🚀 Starting Mental Health App (Production Mode)...")
    print("📱 Access the app at: http://127.0.0.1:5000")
    print("🔧 Using Waitress WSGI server for better Windows compatibility")
    print("-" * 50)
    
    try:
        serve(
            app,
            host='127.0.0.1',
            port=5000,
            threads=4,
            url_scheme='http'
        )
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
