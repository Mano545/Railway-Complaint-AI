from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv

# Add server directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from project root
# Get the project root directory (parent of server directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from routes.complaint import complaint_bp
from services.gemini_service import initialize_gemini

app = Flask(__name__)

# Manual CORS handling (compatible with Python 3.13)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize Gemini AI
initialize_gemini()

# Register blueprints
app.register_blueprint(complaint_bp, url_prefix='/api/complaint')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Railway Complaint AI System is running'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'[SERVER] Running on http://localhost:{port}')
    print(f'[SERVER] Ready to process railway complaint images')
    app.run(host='0.0.0.0', port=port, debug=True)
