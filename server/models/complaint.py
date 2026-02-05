"""
Complaint, location, and train-details models.
"""
from datetime import datetime
from extensions import db


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # RM-YYYYMMDD-XXXXXX
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pending")  # pending, in_progress, resolved
    priority = db.Column(db.String(20), nullable=True)  # CRITICAL, HIGH, MEDIUM, LOW
    issue_category = db.Column(db.String(255), nullable=True)  # AI-predicted or manual
    issue_details = db.Column(db.Text, nullable=True)
    department = db.Column(db.String(255), nullable=True)  # Suggested department
    assigned_department = db.Column(db.String(255), nullable=True)  # Assigned by admin
    ai_confidence = db.Column(db.Float, nullable=True)  # 0–1 from EfficientNet/Gemini
    image_filename = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="complaints")
    location = db.relationship("ComplaintLocation", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    train_details = db.relationship("TrainDetails", back_populates="complaint", uselist=False, cascade="all, delete-orphan")

    def to_dict(self, include_user=False, include_location=True, include_train=True):
        d = {
            "id": self.id,
            "complaintId": self.complaint_id,
            "userId": self.user_id,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "issueCategory": self.issue_category,
            "issueDetails": self.issue_details,
            "department": self.department,
            "assignedDepartment": self.assigned_department,
            "aiConfidence": self.ai_confidence,
            "imageFilename": self.image_filename,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_user and self.user:
            d["user"] = self.user.to_dict(include_email=True)
        if include_location and self.location:
            d["location"] = self.location.to_dict()
        if include_train and self.train_details:
            d["trainDetails"] = self.train_details.to_dict()
        return d


class ComplaintLocation(db.Model):
    __tablename__ = "complaint_locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy_m = db.Column(db.Float, nullable=True)  # GPS accuracy in meters
    nearest_station = db.Column(db.String(255), nullable=True)
    station_proximity_km = db.Column(db.Float, nullable=True)
    railway_context = db.Column(db.Text, nullable=True)  # JSON or text description
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship("Complaint", back_populates="location")

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracyM": self.accuracy_m,
            "nearestStation": self.nearest_station,
            "stationProximityKm": self.station_proximity_km,
            "railwayContext": self.railway_context,
            "capturedAt": self.captured_at.isoformat() if self.captured_at else None,
        }


class TrainDetails(db.Model):
    __tablename__ = "train_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False, index=True)
    train_number = db.Column(db.String(50), nullable=True)
    train_name = db.Column(db.String(255), nullable=True)
    coach_number = db.Column(db.String(50), nullable=True)
    seat_number = db.Column(db.String(50), nullable=True)
    boarding_station = db.Column(db.String(255), nullable=True)
    destination_station = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(50), nullable=True)  # ocr | manual
    raw_ocr_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship("Complaint", back_populates="train_details")

    def to_dict(self):
        return {
            "trainNumber": self.train_number,
            "trainName": self.train_name,
            "coachNumber": self.coach_number,
            "seatNumber": self.seat_number,
            "boardingStation": self.boarding_station,
            "destinationStation": self.destination_station,
            "source": self.source,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
