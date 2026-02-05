"""
Location API: receive GPS, return railway context (nearest station, proximity).
Does not require auth for submission; complaint submission will attach location.
"""
from flask import Blueprint, request, jsonify
from services.location_service import get_nearest_station, build_location_record

location_bp = Blueprint("location", __name__)


@location_bp.route("/resolve", methods=["POST"])
def resolve_location():
    """
    Accept latitude, longitude, optional accuracy_m.
    Return nearest station, proximity, and railway context for storage with complaint.
    """
    data = request.get_json() or {}
    try:
        lat = float(data.get("latitude", data.get("lat")))
        lon = float(data.get("longitude", data.get("lon")))
    except (TypeError, ValueError):
        return jsonify({"error": "latitude and longitude are required and must be numbers"}), 400
    accuracy_m = data.get("accuracy") or data.get("accuracy_m")
    if accuracy_m is not None:
        try:
            accuracy_m = float(accuracy_m)
        except (TypeError, ValueError):
            accuracy_m = None
    ctx = get_nearest_station(lat, lon)
    record = build_location_record(lat, lon, accuracy_m)
    return jsonify({
        "success": True,
        "location": {
            "latitude": record["latitude"],
            "longitude": record["longitude"],
            "accuracyM": record["accuracy_m"],
            "nearestStation": record["nearest_station"],
            "stationProximityKm": record["station_proximity_km"],
            "railwayContext": record["railway_context"],
            "capturedAt": record["captured_at"].isoformat() if record.get("captured_at") else None,
        },
    })
