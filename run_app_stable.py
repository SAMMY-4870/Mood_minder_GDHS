#!/usr/bin/env python3
"""
Stable Flask app runner without auto-reload (recommended for Windows)
"""
import os
import sys
from web_app import app

def main():
    # Set environment variables to minimize issues
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ['FLASK_ENV'] = 'production'  # Use production mode to avoid debug issues
    
    print("🚀 Starting Mental Health App...")
    print("📱 Access the app at: http://127.0.0.1:5000")
    print("⚠️  Note: Auto-reload is disabled for Windows stability")
    print("🔄 To restart after changes, stop (Ctrl+C) and run again")
    print("-" * 50)
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,  # Disable debug mode
            threaded=True,
            use_reloader=False,  # Disable auto-reload
            use_debugger=False   # Disable debugger
        )
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
