from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class IncidentType(str, PyEnum):
    drowsiness = "drowsiness"
    phone_usage = "phone_usage"
    distraction = "distraction"
    no_seatbelt = "no_seatbelt"
    yawning = "yawning"
    critical_risk = "critical_risk"
    no_face = "no_face"
    emotion = "emotion"


class IncidentSeverity(str, PyEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(50), unique=True, index=True, nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    incident_type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.medium)
    description = Column(Text, nullable=True)
    risk_score_at_time = Column(Float, nullable=True)
    ear_value = Column(Float, nullable=True)
    mar_value = Column(Float, nullable=True)
    head_pose = Column(String(50), nullable=True)
    emotion = Column(String(50), nullable=True)
    screenshot_path = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(255), nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trip = relationship("Trip", back_populates="incidents")
    driver = relationship("Driver", back_populates="incidents")

    def __repr__(self):
        return f"<Incident {self.incident_code}: {self.incident_type}>"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    alert_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="medium")
    is_read = Column(Boolean, default=False)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trip = relationship("Trip", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.alert_type}: {self.message[:50]}>"
