from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleStatus

router = APIRouter()


class VehicleCreate(BaseModel):
    plate_number: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    vin: Optional[str] = None
    fuel_type: Optional[str] = "Petrol"
    assigned_driver_id: Optional[int] = None
    camera_installed: Optional[bool] = True
    gps_enabled: Optional[bool] = True
    notes: Optional[str] = None


class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    fuel_type: Optional[str] = None
    status: Optional[VehicleStatus] = None
    assigned_driver_id: Optional[int] = None
    odometer_km: Optional[float] = None
    camera_installed: Optional[bool] = None
    gps_enabled: Optional[bool] = None
    notes: Optional[str] = None


def vehicle_to_dict(v: Vehicle) -> dict:
    return {
        "id": v.id,
        "plate_number": v.plate_number,
        "make": v.make,
        "model": v.model,
        "year": v.year,
        "color": v.color,
        "vin": v.vin,
        "fuel_type": v.fuel_type,
        "status": v.status,
        "assigned_driver_id": v.assigned_driver_id,
        "odometer_km": v.odometer_km,
        "camera_installed": v.camera_installed,
        "gps_enabled": v.gps_enabled,
        "last_service_date": v.last_service_date,
        "next_service_date": v.next_service_date,
        "notes": v.notes,
        "created_at": v.created_at,
    }


@router.get("/")
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    status: Optional[VehicleStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Vehicle)
    if search:
        query = query.where(
            Vehicle.plate_number.ilike(f"%{search}%") |
            Vehicle.make.ilike(f"%{search}%") |
            Vehicle.model.ilike(f"%{search}%")
        )
    if status:
        query = query.where(Vehicle.status == status)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    result = await db.execute(query.offset(skip).limit(limit).order_by(Vehicle.created_at.desc()))
    vehicles = result.scalars().all()
    return {"total": total, "vehicles": [vehicle_to_dict(v) for v in vehicles]}


@router.post("/", status_code=201)
async def create_vehicle(
    data: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vehicle).where(Vehicle.plate_number == data.plate_number))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Plate number already exists")

    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle_to_dict(vehicle)


@router.get("/{vehicle_id}")
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle_to_dict(vehicle)


@router.patch("/{vehicle_id}")
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(vehicle, field, value)

    await db.commit()
    await db.refresh(vehicle)
    return vehicle_to_dict(vehicle)


@router.delete("/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    await db.delete(vehicle)
    await db.commit()
