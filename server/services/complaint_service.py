import os
from datetime import datetime
import random
import string

# In-memory storage (in production, use a database)
complaints = []

def process_complaint(analysis_result, image_filename):
    """
    Process complaint analysis result and create complaint record
    
    Args:
        analysis_result: Result from Gemini Vision API
        image_filename: Original image filename
    
    Returns:
        dict: Complaint object with ID and metadata
    """
    complaint_id = generate_complaint_id()
    timestamp = datetime.now().isoformat()
    
    complaint = {
        'complaintId': complaint_id,
        'timestamp': timestamp,
        'status': 'submitted',
        'issueCategory': analysis_result['issue_category'],
        'issueDetails': analysis_result['issue_details'],
        'priority': analysis_result['priority'],
        'department': analysis_result['department'],
        'complaintDescription': analysis_result['complaint_description'],
        'imageFilename': image_filename,  # Store reference (in production, upload to cloud storage)
        'railMadadStatus': 'pending_integration'  # Conceptual integration status
    }
    
    # Store complaint (in production, save to database)
    complaints.append(complaint)
    
    # Log complaint creation
    print('[INFO] Complaint Details:')
    print(f'   ID: {complaint_id}')
    print(f'   Category: {analysis_result["issue_category"]}')
    print(f'   Priority: {analysis_result["priority"]}')
    print(f'   Department: {analysis_result["department"]}')
    
    # Conceptual Rail Madad integration
    submit_to_rail_madad(complaint)
    
    return complaint

def generate_complaint_id():
    """
    Generate unique complaint ID
    Format: RM-YYYYMMDD-XXXXXX
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'RM-{date_str}-{random_str}'

def submit_to_rail_madad(complaint):
    """
    Conceptual Rail Madad integration
    
    In production, this would:
    1. Authenticate with Rail Madad API
    2. Format complaint according to Rail Madad schema
    3. Submit via REST API
    4. Handle response and update status
    """
    import time
    
    # Simulate API call delay
    time.sleep(0.5)
    
    # Conceptual integration logic
    rail_madad_payload = {
        'complaint_id': complaint['complaintId'],
        'category': complaint['issueCategory'],
        'description': complaint['complaintDescription'],
        'priority': complaint['priority'],
        'department': complaint['department'],
        'timestamp': complaint['timestamp'],
        # Additional fields as per Rail Madad API requirements
        'source': 'ai_automated',
        'metadata': {
            'issue_details': complaint['issueDetails'],
            'image_attached': True
        }
    }
    
    print('[INFO] Rail Madad Integration (Conceptual):')
    print(f'   Would submit to: POST /api/rail-madad/complaints')
    print(f'   Payload: {rail_madad_payload}')
    
    # In production:
    # import requests
    # response = requests.post(
    #     'https://rail-madad-api.gov.in/complaints',
    #     headers={
    #         'Authorization': f'Bearer {os.getenv("RAIL_MADAD_API_KEY")}',
    #         'Content-Type': 'application/json'
    #     },
    #     json=rail_madad_payload
    # )
    # 
    # if response.ok:
    #     result = response.json()
    #     complaint['railMadadStatus'] = 'submitted'
    #     complaint['railMadadId'] = result['id']
    # else:
    #     complaint['railMadadStatus'] = 'failed'
    #     raise Exception('Rail Madad submission failed')
    
    complaint['railMadadStatus'] = 'submitted_conceptually'
    return complaint

def get_complaint_by_id(complaint_id):
    """Get complaint by ID"""
    for complaint in complaints:
        if complaint['complaintId'] == complaint_id:
            return complaint
    return None

def get_all_complaints():
    """Get all complaints (for admin/testing)"""
    return complaints
