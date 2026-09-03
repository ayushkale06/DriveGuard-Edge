from datetime import datetime, date
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class LicenseClass(str, PyEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    CDL = "CDL"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    license_number = Column(String(100), nullable=True)
    license_class = Column(Enum(LicenseClass), nullable=True)
    license_expiry = Column(Date, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    total_trips = Column(Integer, default=0)
    total_distance_km = Column(Float, default=0.0)
    average_risk_score = Column(Float, default=100.0)
    total_incidents = Column(Integer, default=0)
    safety_rating = Column(Float, default=5.0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="driver_profile")
    trips = relationship("Trip", back_populates="driver")
    incidents = relationship("Incident", back_populates="driver")
    vehicles = relationship("Vehicle", back_populates="assigned_driver")

    def __repr__(self):
        return f"<Driver {self.employee_id}: {self.full_name}>"
