from flask import Flask, jsonify
import os
import sys
from dotenv import load_dotenv

# Add server directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

from config import DATABASE_URL
from extensions import db
from routes.complaint import complaint_bp
from routes.auth import auth_bp
from routes.location import location_bp
from routes.ticket import ticket_bp
from routes.admin import admin_bp
from routes.ml import ml_bp
from services.gemini_service import initialize_gemini

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB

db.init_app(app)

# Import models so tables are registered
from models import User, Complaint, ComplaintLocation, TrainDetails  # noqa: E402, F401

with app.app_context():
    db.create_all()
    # Create guest user for unauthenticated complaint submit (optional)
    if User.query.filter_by(email="guest@railway.local").first() is None:
        from services.auth_service import hash_password
        guest = User(
            email="guest@railway.local",
            password_hash=hash_password(os.getenv("GUEST_PASSWORD", "guest")),
            full_name="Guest User",
            role="user",
        )
        db.session.add(guest)
        db.session.commit()
        print("[INFO] Guest user created for anonymous complaint submission")
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        admin_user = User.query.filter_by(email=admin_email).first()
        if admin_user and admin_user.role != "admin":
            admin_user.role = "admin"
            db.session.commit()
            print(f"[INFO] User {admin_email} set as admin")
        elif not admin_user:
            from services.auth_service import hash_password
            admin_user = User(
                email=admin_email,
                password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "admin")),
                full_name="Admin",
                role="admin",
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"[INFO] Admin user created: {admin_email}")

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,PATCH,OPTIONS")
    return response

initialize_gemini()

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(location_bp, url_prefix="/api/location")
app.register_blueprint(ticket_bp, url_prefix="/api/ticket")
app.register_blueprint(complaint_bp, url_prefix="/api/complaint")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(ml_bp, url_prefix="/api/ml")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Railway AI Complaint Management System is running",
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[SERVER] Running on http://localhost:{port}")
    print("[SERVER] Ready: complaint submit, auth, location, ticket OCR, admin")
    app.run(host="0.0.0.0", port=port, debug=True)
