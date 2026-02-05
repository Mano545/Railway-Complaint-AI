"""
Location service: GPS to railway context (nearest station, proximity, track segment).
Uses Haversine distance and a static station list; production can use an external API.
"""
import os
import json
import math
from datetime import datetime
from typing import Optional, Dict, Any

# Haversine formula (km)
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _load_stations(path: Optional[str] = None) -> list:
    path = path or os.getenv("STATIONS_JSON_PATH")
    if not path:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "data", "railway_stations.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_nearest_station(latitude: float, longitude: float, stations_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Find nearest railway station and return railway context.
    Returns: nearest_station_name, station_code, distance_km, railway_context (description).
    """
    stations = _load_stations(stations_path)
    if not stations:
        return {
            "nearest_station": None,
            "station_code": None,
            "station_proximity_km": None,
            "railway_context": "Station data not available.",
        }
    best = None
    best_km = float("inf")
    for s in stations:
        km = haversine_km(latitude, longitude, s["lat"], s["lon"])
        if km < best_km:
            best_km = km
            best = s
    if best is None:
        return {
            "nearest_station": None,
            "station_code": None,
            "station_proximity_km": None,
            "railway_context": "No station found.",
        }
    # Describe proximity
    if best_km < 0.5:
        segment = "at or very close to station premises"
    elif best_km < 2:
        segment = "within station approach / platform area"
    elif best_km < 10:
        segment = "within station vicinity (track segment)"
    else:
        segment = "en route / general area"
    railway_context = (
        f"Nearest station: {best['name']} ({best.get('code', '')}). "
        f"Distance: {best_km:.2f} km. Context: {segment}."
    )
    return {
        "nearest_station": best["name"],
        "station_code": best.get("code"),
        "station_proximity_km": round(best_km, 2),
        "railway_context": railway_context,
    }


def build_location_record(
    latitude: float,
    longitude: float,
    accuracy_m: Optional[float] = None,
    stations_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a dict suitable for ComplaintLocation: lat, lon, accuracy_m,
    nearest_station, station_proximity_km, railway_context, captured_at.
    """
    ctx = get_nearest_station(latitude, longitude, stations_path)
    return {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy_m": accuracy_m,
        "nearest_station": ctx["nearest_station"],
        "station_proximity_km": ctx["station_proximity_km"],
        "railway_context": ctx["railway_context"],
        "captured_at": datetime.utcnow(),
    }
