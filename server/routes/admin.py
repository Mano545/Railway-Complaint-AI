"""
Admin and department dashboard API: list/filter complaints, map view, assign, insights.
Requires role admin or department.
"""
from flask import Blueprint, request, jsonify
from services.auth_service import decode_token
from services.complaint_service import (
    get_all_complaints,
    get_complaints_for_map,
    update_complaint_status,
    assign_department,
    get_insights,
)
from config import ROLE_ADMIN, ROLE_DEPARTMENT

admin_bp = Blueprint("admin", __name__)


def _require_admin_or_department():
    """Return (user_id, role) if JWT is admin or department; else None."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    payload = decode_token(auth[7:])
    if not payload or payload.get("type") != "access":
        return None
    role = payload.get("role")
    if role not in (ROLE_ADMIN, ROLE_DEPARTMENT):
        return None
    try:
        return int(payload.get("sub")), role
    except (TypeError, ValueError):
        return None


@admin_bp.route("/complaints", methods=["GET"])
def list_complaints():
    """
    List all complaints with optional filters: station, train_number, issue_type, status.
    Query params: station, train_number, issue_type, status, limit, offset.
    """
    if _require_admin_or_department() is None:
        return jsonify({"error": "Admin or department access required"}), 403
    station = request.args.get("station")
    train_number = request.args.get("train_number")
    issue_type = request.args.get("issue_type")
    status = request.args.get("status")
    limit = min(int(request.args.get("limit", 100)), 500)
    offset = max(0, int(request.args.get("offset", 0)))
    complaints = get_all_complaints(
        station=station,
        train_number=train_number,
        issue_type=issue_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return jsonify({
        "success": True,
        "complaints": [c.to_dict(include_user=True, include_location=True, include_train=True) for c in complaints],
        "count": len(complaints),
    })


@admin_bp.route("/complaints/map", methods=["GET"])
def complaints_map():
    """Complaints with lat/lon for map/heatmap view."""
    if _require_admin_or_department() is None:
        return jsonify({"error": "Admin or department access required"}), 403
    limit = min(int(request.args.get("limit", 500)), 1000)
    points = get_complaints_for_map(limit=limit)
    return jsonify({"success": True, "points": points})


@admin_bp.route("/complaints/<complaint_id>/status", methods=["PATCH", "PUT"])
def set_status(complaint_id):
    """Update complaint status: pending, in_progress, resolved."""
    if _require_admin_or_department() is None:
        return jsonify({"error": "Admin or department access required"}), 403
    data = request.get_json() or {}
    status = data.get("status")
    if not status:
        return jsonify({"error": "status is required"}), 400
    complaint = update_complaint_status(complaint_id, status)
    if not complaint:
        return jsonify({"error": "Complaint not found or invalid status"}), 404
    return jsonify({"success": True, "complaint": complaint.to_dict(include_user=False, include_location=True, include_train=True)})


@admin_bp.route("/complaints/<complaint_id>/assign", methods=["PATCH", "PUT"])
def assign_dept(complaint_id):
    """Assign complaint to department."""
    if _require_admin_or_department() is None:
        return jsonify({"error": "Admin or department access required"}), 403
    data = request.get_json() or {}
    department = data.get("department") or data.get("assignedDepartment")
    if not department:
        return jsonify({"error": "department is required"}), 400
    complaint = assign_department(complaint_id, department)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404
    return jsonify({"success": True, "complaint": complaint.to_dict(include_user=False, include_location=True, include_train=True)})


@admin_bp.route("/insights", methods=["GET"])
def insights():
    """AI insights: counts by category, status, priority (for dashboards)."""
    if _require_admin_or_department() is None:
        return jsonify({"error": "Admin or department access required"}), 403
    data = get_insights()
    return jsonify({"success": True, "insights": data})
