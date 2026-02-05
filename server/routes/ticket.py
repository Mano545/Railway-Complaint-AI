"""
Ticket OCR API: upload ticket image/PDF, get structured train details.
"""
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import ALLOWED_TICKET_EXTENSIONS, UPLOAD_FOLDER
from services.ocr_service import extract_train_details_from_ticket

ticket_bp = Blueprint("ticket", __name__)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_ticket(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_TICKET_EXTENSIONS


@ticket_bp.route("/extract", methods=["POST"])
def extract_ticket():
    """
    Upload ticket (image or PDF). Returns train_number, train_name, coach_number,
    seat_number, boarding_station, destination_station, raw_ocr_text.
    """
    if "ticket" not in request.files and "file" not in request.files:
        return jsonify({"error": "Ticket file (ticket or file) is required"}), 400
    file = request.files.get("ticket") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_ticket(file.filename):
        return jsonify({
            "error": f"Allowed formats: {', '.join(ALLOWED_TICKET_EXTENSIONS)}"
        }), 400
    data = file.read()
    try:
        details = extract_train_details_from_ticket(data, file.filename)
    except Exception as e:
        return jsonify({"error": "OCR failed", "message": str(e)}), 500
    # Return camelCase for frontend
    return jsonify({
        "success": True,
        "trainDetails": {
            "trainNumber": details.get("train_number"),
            "trainName": details.get("train_name"),
            "coachNumber": details.get("coach_number"),
            "seatNumber": details.get("seat_number"),
            "boardingStation": details.get("boarding_station"),
            "destinationStation": details.get("destination_station"),
            "source": details.get("source", "ocr"),
            "rawOcrText": details.get("raw_ocr_text"),
        },
    })
