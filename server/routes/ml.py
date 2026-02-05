"""
ML inference API: EfficientNet image classification with confidence score.
"""
import os
from flask import Blueprint, request, jsonify
from services.ml_inference_service import predict_issue_from_image, map_effnet_to_department, map_effnet_to_priority
from config import ALLOWED_IMAGE_EXTENSIONS

ml_bp = Blueprint("ml", __name__)


def _allowed(filename):
    ext = (filename or "").rsplit(".", 1)[-1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


@ml_bp.route("/predict", methods=["POST"])
def predict():
    """
    Upload image; returns issue_category, confidence, all_probs, suggested department/priority.
    """
    if "image" not in request.files and "file" not in request.files:
        return jsonify({"error": "Image file (image or file) is required"}), 400
    file = request.files.get("image") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not _allowed(file.filename):
        return jsonify({"error": "Allowed: png, jpg, jpeg, gif, webp, jfif"}), 400
    data = file.read()
    result = predict_issue_from_image(data)
    if result.get("model_used") is None:
        return jsonify({
            "success": False,
            "message": "ML model not loaded. Train with ml/train_railway_model.py",
            "issue_category": None,
            "confidence": 0,
            "all_probs": {},
        })
    category = result.get("issue_category")
    return jsonify({
        "success": True,
        "issue_category": category,
        "confidence": result.get("confidence", 0),
        "all_probs": result.get("all_probs", {}),
        "suggested_department": map_effnet_to_department(category) if category else None,
        "suggested_priority": map_effnet_to_priority(category) if category else None,
    })
