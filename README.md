# 🚂 Railway Complaint AI System

An AI-powered Railway Complaint Management System inspired by Rail Madad. Upload an image of a railway issue, and the system automatically analyzes, classifies, and files your complaint using Google's Gemini Vision API.

## 🌟 Features

- **AI-Powered Image Analysis**: Uses Gemini Vision API to understand railway issues from images
- **Automatic Classification**: Classifies issues into 9 predefined categories
- **Smart Priority Assignment**: Assigns priority levels (CRITICAL, HIGH, MEDIUM, LOW) based on issue severity
- **Department Routing**: Automatically routes complaints to the appropriate department
- **Structured Complaint Generation**: Creates professional complaint descriptions ready for filing
- **Modern UI**: Beautiful, responsive React frontend with intuitive user experience

## 📋 Supported Issue Categories

1. **Overcrowding & Crowd Management**
2. **Cleanliness, Sanitation & Hygiene** (Highest priority)
3. **Water & Drinking Facilities**
4. **Food & Vendor Issues**
5. **Faulty Amenities & Infrastructure**
6. **Safety & Security Concerns**
7. **Accessibility & Passenger Assistance**
8. **Information & Communication Gaps**
9. **Other / Miscellaneous**

## 🏗️ Architecture

```
Frontend (React) 
    ↓
Backend (Python + Flask)
    ↓
Gemini Vision API (Image Analysis)
    ↓
Backend (Complaint Processing)
    ↓
Rail Madad System (Conceptual Integration)
```

### Key Components

- **Frontend**: React application with image upload and result display
- **Backend API**: Flask server handling image uploads and AI processing
- **Gemini Service**: Integration with Google Gemini Vision API for image analysis
- **Complaint Service**: Processes AI results and creates structured complaints

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js (v14 or higher) - for React frontend only
- npm or yarn - for React frontend only
- pip (Python package manager)
- Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd railway-complaint-ai
   ```

2. **Install dependencies**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install frontend dependencies
   cd client && npm install && cd ..
   
   # Or use the convenience script (requires npm)
   npm run install-all
   ```
   This installs dependencies for both backend (Python) and frontend (React).

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Start the development servers**
   ```bash
   npm run dev
   ```
   This starts both backend (Flask on port 5000) and frontend (React on port 3000) concurrently.

   Or start them separately:
   ```bash
   # Terminal 1 - Backend (Python Flask)
   cd server && python app.py

   # Terminal 2 - Frontend (React)
   cd client && npm start
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
railway-complaint-ai/
├── server/
│   ├── app.py                   # Flask server entry point
│   ├── routes/
│   │   └── complaint.py         # Complaint API routes
│   └── services/
│       ├── gemini_service.py    # Gemini Vision API integration
│       └── complaint_service.py # Complaint processing logic
├── requirements.txt             # Python dependencies
├── client/
│   ├── public/
│   ├── src/
│   │   ├── App.js               # Main React component
│   │   ├── components/
│   │   │   ├── ComplaintForm.js    # Image upload form
│   │   │   └── ComplaintResult.js   # Results display
│   │   └── index.js
│   └── package.json
├── uploads/                     # Temporary image storage (gitignored)
├── .env.example                 # Environment variables template
├── .gitignore
├── package.json                 # Root package.json
└── README.md
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `PORT`: Backend server port (default: 5000)

### Python Dependencies

Key Python packages used:
- `Flask`: Web framework for the API
- `flask-cors`: CORS support for frontend-backend communication
- `google-generativeai`: Gemini Vision API client
- `Pillow`: Image processing
- `python-dotenv`: Environment variable management

### API Endpoints

- `POST /api/complaint/submit`: Submit a complaint with image
  - Body: `multipart/form-data`
  - Fields:
    - `image` (file, required): Image file (max 10MB)
    - `text` (string, optional): Additional context
  - Response: Complaint object with ID, category, priority, etc.

- `GET /api/health`: Health check endpoint

## 🎯 How It Works

1. **User Uploads Image**: User selects an image showing a railway issue
2. **Optional Text Input**: User can provide additional context
3. **Image Analysis**: Backend sends image to Gemini Vision API with structured prompt
4. **AI Classification**: Gemini analyzes the image and returns:
   - Issue category
   - Issue details
   - Priority level
   - Department routing
   - Complaint description
5. **Complaint Creation**: Backend processes the AI response and creates a complaint
6. **Rail Madad Integration**: Complaint is prepared for submission to Rail Madad (conceptual)
7. **Result Display**: User sees the generated complaint with all details

## 🔐 Security Considerations

- **API Key Protection**: Never commit `.env` file with real API keys
- **File Upload Limits**: 10MB file size limit enforced
- **File Type Validation**: Only image files (jpeg, jpg, png, gif, webp) accepted
- **Temporary Storage**: Uploaded files are deleted after processing
- **No Direct LLM Access**: Frontend never directly contacts Gemini API

## 🧪 Testing

### Sample Test Flow

1. Upload an image of a dirty railway toilet
2. System should classify as "Cleanliness, Sanitation & Hygiene"
3. Priority should be "HIGH" or "MEDIUM"
4. Department should be "Housekeeping & Sanitation"
5. Complaint description should be generated automatically

## 🔮 Future Enhancements

- [ ] Database integration (MongoDB/PostgreSQL) for complaint storage
- [ ] Real Rail Madad API integration
- [ ] User authentication and complaint history
- [ ] Email/SMS notifications
- [ ] Admin dashboard for complaint management
- [ ] Multi-language support
- [ ] Image preprocessing and optimization
- [ ] Batch complaint processing
- [ ] Analytics and reporting

## 📝 Priority Assignment Rules

- **CRITICAL**: Fire, security threats, harassment, stampede risk
- **HIGH**: Overcrowding, safety risks, accessibility issues
- **MEDIUM**: AC failure, toilet overflow, water issues
- **LOW**: Cleanliness issues without immediate risk

## 🏢 Department Routing

- Fire/Security/Harassment → Emergency Services / GRP / RPF
- Cleanliness/Toilets/Waste → Housekeeping & Sanitation
- AC/Fans/Electrical → Electrical & Maintenance
- Food/Vendors → Catering & Railway Administration
- Overcrowding/Crowd Control → Railway Administration
- Accessibility Issues → Station Management
- Information Issues → Operations & Control Room

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for your own purposes.

## 🙏 Acknowledgments

- Inspired by Rail Madad complaint system
- Powered by Google Gemini Vision API
- Built with React and Node.js

## 📞 Support

For issues or questions, please open an issue on the repository.

---

**Note**: This is a conceptual implementation. The Rail Madad integration is simulated. In production, you would need to integrate with the actual Rail Madad API using their official documentation and authentication mechanisms.
