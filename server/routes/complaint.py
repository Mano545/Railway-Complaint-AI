from flask import Blueprint, request, jsonify
import os
import base64
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from services.gemini_service import analyze_image
from services.complaint_service import process_complaint

complaint_bp = Blueprint('complaint', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@complaint_bp.route('/submit', methods=['POST'])
def submit_complaint():
    """Handle complaint submission with image"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'Image file is required'}), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Only image files are allowed (jpeg, jpg, png, gif, webp)'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB'
            }), 400
        
        # Get additional text if provided
        additional_text = request.form.get('text', '')
        
        # Read image data
        image_data = file.read()
        mime_type = file.content_type or 'image/jpeg'
        
        print('[INFO] Processing complaint with image...')
        print(f'[INFO] Additional text: {additional_text or "None"}')
        
        # Analyze image with Gemini Vision API
        analysis_result = analyze_image(image_data, mime_type, additional_text)
        
        # Process and create complaint
        complaint = process_complaint(analysis_result, file.filename)
        
        print(f'[OK] Complaint created: {complaint["complaintId"]}')
        
        return jsonify({
            'success': True,
            'complaint': complaint
        })
        
    except RequestEntityTooLarge:
        return jsonify({
            'error': 'File size exceeds maximum limit'
        }), 400
    except Exception as e:
        print(f'[ERROR] Error processing complaint: {str(e)}')
        return jsonify({
            'error': 'Failed to process complaint',
            'message': str(e)
        }), 500
