import os
import json
import re
from google import generativeai as genai
from dotenv import load_dotenv

# Global model variable
model = None

def initialize_gemini():
    """Initialize Gemini AI client"""
    global model
    
    # Ensure .env is loaded (in case called before app.py loads it)
    # Get project root (parent of server directory)
    current_file = os.path.abspath(__file__)
    server_dir = os.path.dirname(os.path.dirname(current_file))
    project_root = os.path.dirname(server_dir)
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print('WARNING: GEMINI_API_KEY not found in environment variables')
        print('WARNING: Please set GEMINI_API_KEY in your .env file')
        return
    
    try:
        genai.configure(api_key=api_key)
        # Use gemini-2.5-flash (gemini-1.5-flash is deprecated/removed)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        model = genai.GenerativeModel(model_name)
        print(f'[OK] Gemini AI initialized (model: {model_name})')
    except Exception as error:
        print(f'[ERROR] Failed to initialize Gemini AI: {error}')
        raise error

def analyze_image(image_data, mime_type, additional_text=''):
    """
    Analyze image using Gemini Vision API
    
    Args:
        image_data: Image file bytes
        mime_type: Image MIME type
        additional_text: Optional additional text from user
    
    Returns:
        dict: Structured analysis result
    """
    if not model:
        raise Exception('Gemini AI not initialized. Please set GEMINI_API_KEY in .env')
    
    # Build the structured prompt
    prompt = build_analysis_prompt(additional_text)
    
    try:
        # Prepare image part
        import PIL.Image
        import io
        
        # Convert bytes to PIL Image
        image = PIL.Image.open(io.BytesIO(image_data))
        
        # Generate content
        response = model.generate_content([prompt, image])
        text = response.text
        
        # Parse JSON response
        analysis_result = parse_analysis_response(text)
        
        return analysis_result
    except Exception as error:
        print(f'Error analyzing image with Gemini: {error}')
        raise Exception(f'AI analysis failed: {str(error)}')

def build_analysis_prompt(additional_text):
    """Build structured prompt for Gemini Vision API"""
    prompt = """You are an expert railway complaint analyst. Analyze the uploaded image and classify the railway issue.

RAILWAY ISSUE CATEGORIES (select ONE):
1. Overcrowding & Crowd Management
2. Cleanliness, Sanitation & Hygiene
3. Water & Drinking Facilities
4. Food & Vendor Issues
5. Faulty Amenities & Infrastructure
6. Safety & Security Concerns
7. Accessibility & Passenger Assistance
8. Information & Communication Gaps
9. Other / Miscellaneous

PRIORITY LEVELS:
- CRITICAL: Fire, security threats, harassment, stampede risk
- HIGH: Overcrowding, safety risks, accessibility issues
- MEDIUM: AC failure, toilet overflow, water issues
- LOW: Cleanliness issues without immediate risk

DEPARTMENT ROUTING:
- Fire/Security/Harassment → Emergency Services / GRP / RPF
- Cleanliness/Toilets/Waste → Housekeeping & Sanitation
- AC/Fans/Electrical → Electrical & Maintenance
- Food/Vendors → Catering & Railway Administration
- Overcrowding/Crowd Control → Railway Administration
- Accessibility Issues → Station Management
- Information Issues → Operations & Control Room

"""
    
    if additional_text:
        prompt += f'ADDITIONAL USER CONTEXT: "{additional_text}"\n\n'
    
    prompt += """TASK:
1. Visually analyze the image
2. Identify the railway issue shown
3. Classify into ONE of the 9 categories above
4. Assign priority (CRITICAL, HIGH, MEDIUM, or LOW)
5. Determine the appropriate department
6. Generate a detailed complaint description

IMPORTANT: Return ONLY valid JSON in this exact format (no markdown, no explanations):
{
  "issue_category": "exact category name from list above",
  "issue_details": "detailed description of what you see in the image",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",
  "department": "exact department name from routing rules",
  "complaint_description": "professional complaint text suitable for official filing"
}

Return ONLY the JSON object, nothing else."""
    
    return prompt

def parse_analysis_response(text):
    """
    Parse and validate Gemini response
    
    Args:
        text: Raw response text from Gemini
    
    Returns:
        dict: Parsed and validated analysis result
    """
    try:
        # Remove markdown code blocks if present
        json_text = text.strip()
        json_text = re.sub(r'```json\n?', '', json_text)
        json_text = re.sub(r'```\n?', '', json_text)
        json_text = json_text.strip()
        
        # Find JSON object in response
        json_match = re.search(r'\{[\s\S]*\}', json_text)
        if not json_match:
            raise Exception('No JSON object found in response')
        
        parsed = json.loads(json_match.group(0))
        
        # Validate required fields
        required_fields = [
            'issue_category',
            'issue_details',
            'priority',
            'department',
            'complaint_description'
        ]
        
        for field in required_fields:
            if field not in parsed:
                raise Exception(f'Missing required field: {field}')
        
        # Validate priority
        valid_priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        if parsed['priority'] not in valid_priorities:
            raise Exception(f'Invalid priority: {parsed["priority"]}')
        
        return parsed
    except Exception as error:
        print(f'Failed to parse Gemini response: {error}')
        print(f'Raw response: {text}')
        raise Exception(f'Failed to parse AI response: {str(error)}')
