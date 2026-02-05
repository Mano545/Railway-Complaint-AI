"""
Complaint submission and retrieval: image + optional location, train details, JWT.
Uses EfficientNet when model exists, else Gemini for issue analysis.
"""
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from extensions import db
from models import User
from config import UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS
from services.gemini_service import analyze_image
from services.complaint_service import (
    create_complaint,
    get_complaint_by_id,
    get_complaints_by_user,
)
from services.location_service import build_location_record
from services.ml_inference_service import (
    predict_issue_from_image,
    map_effnet_to_department,
    map_effnet_to_priority,
)

complaint_bp = Blueprint("complaint", __name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_IMAGE_EXTENSIONS


def _get_user_id_from_request():
    """Return user_id from JWT if present, else None."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    from services.auth_service import decode_token
    payload = decode_token(auth[7:])
    if not payload or payload.get("type") != "access":
        return None
    try:
        return int(payload.get("sub"))
    except (TypeError, ValueError):
        return None


def _get_analysis_result(image_data: bytes, mime_type: str, additional_text: str):
    """Run EfficientNet first; if confidence >= 0.5 use it, else Gemini."""
    ml_result = predict_issue_from_image(image_data)
    if ml_result.get("model_used") and ml_result.get("confidence", 0) >= 0.5:
        category = ml_result.get("issue_category") or "Other"
        return {
            "issue_category": category.replace("_", " ").title(),
            "issue_details": f"AI-detected: {category}",
            "priority": map_effnet_to_priority(category),
            "department": map_effnet_to_department(category),
            "complaint_description": additional_text or f"Issue category: {category}",
            "ai_confidence": ml_result.get("confidence"),
        }
    # Fallback to Gemini
    try:
        result = analyze_image(image_data, mime_type, additional_text)
        result["ai_confidence"] = None  # Gemini doesn't return numeric confidence
        return result
    except Exception as e:
        print(f"[WARN] Gemini fallback failed: {e}")
        return {
            "issue_category": "Other / Miscellaneous",
            "issue_details": str(e),
            "priority": "MEDIUM",
            "department": "Railway Administration",
            "complaint_description": additional_text or "Image analysis unavailable.",
            "ai_confidence": None,
        }


@complaint_bp.route("/submit", methods=["POST"])
def submit_complaint():
    """
    Submit complaint with image. Optional: location (lat/lon/accuracy), train_details (JSON),
    text (description). If Authorization Bearer present, complaint is linked to that user.
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "Image file is required"}), 400
        file = request.files["image"]
        if not file or file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Only image files allowed (jpeg, jpg, png, gif, webp, jfif)"}), 400
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": f"File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB"}), 400

        user_id = _get_user_id_from_request()
        if user_id is None:
            # Optional: use a default "guest" user if you want to allow unauthenticated submit
            guest = User.query.filter_by(email="guest@railway.local").first()
            if guest:
                user_id = guest.id
            else:
                return jsonify({"error": "Authentication required. Please login or register."}), 401

        additional_text = request.form.get("text", "")
        # Location: form fields only (submit is multipart/form-data)
        location_data = None
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        if lat is not None and lon is not None:
            try:
                lat, lon = float(lat), float(lon)
                acc = request.form.get("accuracy") or request.form.get("accuracy_m")
                acc = float(acc) if acc is not None else None
                location_data = build_location_record(lat, lon, acc)
            except (TypeError, ValueError):
                pass

        # Train details: form field (JSON string from ticket OCR or manual)
        train_details_data = None
        td_json = request.form.get("train_details") or request.form.get("trainDetails")
        if td_json:
            try:
                import json
                train_details_data = json.loads(td_json)
            except Exception:
                pass

        image_data = file.read()
        mime_type = file.content_type or "image/jpeg"
        analysis_result = _get_analysis_result(image_data, mime_type, additional_text)
        safe_filename = secure_filename(file.filename) or "image.jpg"

        complaint = create_complaint(
            user_id=user_id,
            analysis_result=analysis_result,
            image_filename=safe_filename,
            location_data=location_data,
            train_details_data=train_details_data,
            description_override=additional_text or None,
        )
        return jsonify({
            "success": True,
            "complaint": complaint.to_dict(include_user=False, include_location=True, include_train=True),
        })
    except RequestEntityTooLarge:
        return jsonify({"error": "File size exceeds limit"}), 400
    except Exception as e:
        print(f"[ERROR] Complaint submit: {e}")
        return jsonify({"error": "Failed to process complaint", "message": str(e)}), 500


@complaint_bp.route("/<complaint_id>", methods=["GET"])
def get_complaint(complaint_id):
    """Get single complaint by RM-... id."""
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404
    return jsonify({"success": True, "complaint": complaint.to_dict(include_user=True, include_location=True, include_train=True)})


@complaint_bp.route("/my", methods=["GET"])
def my_complaints():
    """List complaints for current user (requires JWT)."""
    user_id = _get_user_id_from_request()
    if user_id is None:
        return jsonify({"error": "Authentication required"}), 401
    complaints = get_complaints_by_user(user_id)
    return jsonify({
        "success": True,
        "complaints": [c.to_dict(include_user=False, include_location=True, include_train=True) for c in complaints],
    })
