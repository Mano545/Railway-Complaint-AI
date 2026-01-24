#!/usr/bin/env python3
"""
Convenience script to run the Flask server
"""
import os
import sys

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'🚂 Server running on http://localhost:{port}')
    print(f'📸 Ready to process railway complaint images')
    app.run(host='0.0.0.0', port=port, debug=True)
