"""
Complaint service: create and query complaints with location, train details, and AI analysis.
Uses database (SQLAlchemy); supports both EfficientNet and Gemini analysis.
"""
import os
import random
import string
from datetime import datetime
from typing import Optional, Dict, Any, List

from extensions import db
from models import Complaint, ComplaintLocation, TrainDetails
from config import STATUS_PENDING


def generate_complaint_id() -> str:
    """Format: RM-YYYYMMDD-XXXXXX"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"RM-{date_str}-{random_str}"


def _ensure_unique_id() -> str:
    cid = generate_complaint_id()
    while Complaint.query.filter_by(complaint_id=cid).first():
        cid = generate_complaint_id()
    return cid


def create_complaint(
    user_id: int,
    analysis_result: Dict[str, Any],
    image_filename: Optional[str] = None,
    location_data: Optional[Dict[str, Any]] = None,
    train_details_data: Optional[Dict[str, Any]] = None,
    description_override: Optional[str] = None,
) -> Complaint:
    """
    Create complaint with optional location and train details.
    analysis_result must have: issue_category, issue_details, priority, department, complaint_description
    (and optionally ai_confidence).
    """
    complaint_id = _ensure_unique_id()
    desc = description_override or analysis_result.get("complaint_description") or ""
    priority = analysis_result.get("priority")
    issue_category = analysis_result.get("issue_category")
    issue_details = analysis_result.get("issue_details")
    department = analysis_result.get("department")
    ai_confidence = analysis_result.get("ai_confidence")

    complaint = Complaint(
        complaint_id=complaint_id,
        user_id=user_id,
        description=desc,
        status=STATUS_PENDING,
        priority=priority,
        issue_category=issue_category,
        issue_details=issue_details,
        department=department,
        ai_confidence=ai_confidence,
        image_filename=image_filename,
    )
    db.session.add(complaint)
    db.session.flush()  # get complaint.id

    if location_data:
        loc = ComplaintLocation(
            complaint_id=complaint.id,
            latitude=location_data["latitude"],
            longitude=location_data["longitude"],
            accuracy_m=location_data.get("accuracy_m"),
            nearest_station=location_data.get("nearest_station"),
            station_proximity_km=location_data.get("station_proximity_km"),
            railway_context=location_data.get("railway_context"),
            captured_at=location_data.get("captured_at") or datetime.utcnow(),
        )
        db.session.add(loc)

    if train_details_data:
        td = TrainDetails(
            complaint_id=complaint.id,
            train_number=train_details_data.get("train_number") or train_details_data.get("trainNumber"),
            train_name=train_details_data.get("train_name") or train_details_data.get("trainName"),
            coach_number=train_details_data.get("coach_number") or train_details_data.get("coachNumber"),
            seat_number=train_details_data.get("seat_number") or train_details_data.get("seatNumber"),
            boarding_station=train_details_data.get("boarding_station") or train_details_data.get("boardingStation"),
            destination_station=train_details_data.get("destination_station") or train_details_data.get("destinationStation"),
            source=train_details_data.get("source", "manual"),
            raw_ocr_text=train_details_data.get("raw_ocr_text") or train_details_data.get("rawOcrText"),
        )
        db.session.add(td)

    db.session.commit()
    db.session.refresh(complaint)
    return complaint


def get_complaint_by_id(complaint_id: str) -> Optional[Complaint]:
    """Get complaint by RM-... id."""
    return Complaint.query.filter_by(complaint_id=complaint_id).first()


def get_complaint_by_db_id(complaint_db_id: int) -> Optional[Complaint]:
    return Complaint.query.get(complaint_db_id)


def get_complaints_by_user(user_id: int) -> List[Complaint]:
    return Complaint.query.filter_by(user_id=user_id).order_by(Complaint.created_at.desc()).all()


def get_all_complaints(
    station: Optional[str] = None,
    train_number: Optional[str] = None,
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Complaint]:
    """Admin: list complaints with optional filters."""
    q = Complaint.query
    if status:
        q = q.filter(Complaint.status == status)
    if issue_type:
        q = q.filter(Complaint.issue_category == issue_type)
    if station:
        q = q.join(ComplaintLocation, Complaint.id == ComplaintLocation.complaint_id).filter(
            db.or_(
                ComplaintLocation.nearest_station.ilike(f"%{station}%"),
                ComplaintLocation.railway_context.ilike(f"%{station}%"),
            )
        )
    if train_number:
        q = q.join(TrainDetails, Complaint.id == TrainDetails.complaint_id).filter(
            db.or_(
                TrainDetails.train_number == train_number,
                TrainDetails.train_number.ilike(f"%{train_number}%"),
            )
        )
    return q.order_by(Complaint.created_at.desc()).limit(limit).offset(offset).all()


def get_complaints_for_map(limit: int = 500) -> List[Dict[str, Any]]:
    """Complaints with location for map view."""
    q = (
        Complaint.query.join(ComplaintLocation, Complaint.id == ComplaintLocation.complaint_id)
        .with_entities(Complaint, ComplaintLocation)
        .order_by(Complaint.created_at.desc())
        .limit(limit)
    )
    rows = q.all()
    out = []
    for complaint, loc in rows:
        out.append({
            "complaintId": complaint.complaint_id,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "status": complaint.status,
            "priority": complaint.priority,
            "issueCategory": complaint.issue_category,
            "nearestStation": loc.nearest_station,
        })
    return out


def update_complaint_status(complaint_id: str, status: str) -> Optional[Complaint]:
    from config import COMPLAINT_STATUSES
    if status not in COMPLAINT_STATUSES:
        return None
    c = get_complaint_by_id(complaint_id)
    if not c:
        return None
    c.status = status
    db.session.commit()
    db.session.refresh(c)
    return c


def assign_department(complaint_id: str, department: str) -> Optional[Complaint]:
    c = get_complaint_by_id(complaint_id)
    if not c:
        return None
    c.assigned_department = department
    db.session.commit()
    db.session.refresh(c)
    return c


def get_insights() -> Dict[str, Any]:
    """AI insights: counts by category, status, priority; optional heatmap data."""
    from sqlalchemy import func
    by_category = (
        db.session.query(Complaint.issue_category, func.count(Complaint.id))
        .filter(Complaint.issue_category.isnot(None))
        .group_by(Complaint.issue_category)
        .all()
    )
    by_status = (
        db.session.query(Complaint.status, func.count(Complaint.id))
        .group_by(Complaint.status)
        .all()
    )
    by_priority = (
        db.session.query(Complaint.priority, func.count(Complaint.id))
        .filter(Complaint.priority.isnot(None))
        .group_by(Complaint.priority)
        .all()
    )
    return {
        "byCategory": {k: v for k, v in by_category},
        "byStatus": {k: v for k, v in by_status},
        "byPriority": {k: v for k, v in by_priority},
    }
