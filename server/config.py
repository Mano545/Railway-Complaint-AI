"""
Application configuration for Railway AI Complaint Management System.
Supports environment-based settings and secure defaults.
"""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{PROJECT_ROOT / 'railway_complaints.db'}"
)
# SQLite doesn't use this; PostgreSQL does
if DATABASE_URL.startswith("postgresql://") and "?" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql://", 1)

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production-use-env")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "60"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))

# Uploads
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(PROJECT_ROOT / "uploads"))
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "jfif"}
ALLOWED_TICKET_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

# ML model paths (relative to project root)
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", str(PROJECT_ROOT / "railway_issue_model.h5"))
ML_CLASSES_PATH = os.getenv("ML_CLASSES_PATH", str(PROJECT_ROOT / "railway_model_classes.json"))

# OCR: prefer EasyOCR for better accuracy; fallback to Tesseract
OCR_ENGINE = os.getenv("OCR_ENGINE", "easyocr")  # easyocr | tesseract

# Station data for nearest-station resolution
STATIONS_JSON_PATH = os.getenv("STATIONS_JSON_PATH", str(BASE_DIR / "data" / "railway_stations.json"))

# Roles
ROLE_USER = "user"
ROLE_DEPARTMENT = "department"
ROLE_ADMIN = "admin"
ROLES = [ROLE_USER, ROLE_DEPARTMENT, ROLE_ADMIN]

# Complaint status
STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_RESOLVED = "resolved"
COMPLAINT_STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_RESOLVED]

# Priority
PRIORITY_CRITICAL = "CRITICAL"
PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_LOW = "LOW"
PRIORITIES = [PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW]
