from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class TripStatus(str, PyEnum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
    paused = "paused"


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    trip_code = Column(String(50), unique=True, index=True, nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    status = Column(Enum(TripStatus), default=TripStatus.active)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    distance_km = Column(Float, default=0.0)
    start_location = Column(String(255), nullable=True)
    end_location = Column(String(255), nullable=True)
    start_lat = Column(Float, nullable=True)
    start_lng = Column(Float, nullable=True)
    end_lat = Column(Float, nullable=True)
    end_lng = Column(Float, nullable=True)

    # AI Monitoring Stats
    average_risk_score = Column(Float, default=100.0)
    min_risk_score = Column(Float, default=100.0)
    max_risk_score = Column(Float, default=100.0)
    total_blinks = Column(Integer, default=0)
    total_yawns = Column(Integer, default=0)
    drowsy_events = Column(Integer, default=0)
    phone_events = Column(Integer, default=0)
    distraction_events = Column(Integer, default=0)
    no_seatbelt_events = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    frames_processed = Column(Integer, default=0)

    # Safety Score (0-100)
    safety_score = Column(Float, default=100.0)

    notes = Column(Text, nullable=True)
    route_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    driver = relationship("Driver", back_populates="trips")
    vehicle = relationship("Vehicle", back_populates="trips")
    incidents = relationship("Incident", back_populates="trip")
    alerts = relationship("Alert", back_populates="trip")

    def __repr__(self):
        return f"<Trip {self.trip_code}>"
