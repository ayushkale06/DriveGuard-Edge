from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class VehicleStatus(str, PyEnum):
    active = "active"
    maintenance = "maintenance"
    inactive = "inactive"
    retired = "retired"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(50), unique=True, index=True, nullable=False)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String(50), nullable=True)
    vin = Column(String(100), unique=True, nullable=True)
    fuel_type = Column(String(50), default="Petrol")
    status = Column(Enum(VehicleStatus), default=VehicleStatus.active)
    assigned_driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    odometer_km = Column(Float, default=0.0)
    camera_installed = Column(Boolean, default=True)
    gps_enabled = Column(Boolean, default=True)
    last_service_date = Column(DateTime, nullable=True)
    next_service_date = Column(DateTime, nullable=True)
    insurance_expiry = Column(DateTime, nullable=True)
    image_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_driver = relationship("Driver", back_populates="vehicles")
    trips = relationship("Trip", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle {self.plate_number}: {self.year} {self.make} {self.model}>"
