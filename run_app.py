#!/usr/bin/env python3
"""
Enhanced Flask app runner with Windows compatibility fixes
"""
import os
import sys
from web_app import app

def main():
    # Set environment variables to fix common issues
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable TensorFlow oneDNN warnings
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Windows-specific fixes
    if sys.platform.startswith('win'):
        # Disable TensorFlow file monitoring to prevent excessive reloads
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging
        
        # Use threaded mode for better Windows compatibility
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False,  # Disable auto-reloader to prevent socket issues
            use_debugger=True
        )
    else:
        # Standard configuration for other platforms
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            threaded=True
        )

if __name__ == '__main__':
    main()
