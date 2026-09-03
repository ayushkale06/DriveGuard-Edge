from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.driver import Driver, LicenseClass

router = APIRouter()


class DriverCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_class: Optional[LicenseClass] = None
    license_expiry: Optional[date] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None


class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_class: Optional[LicenseClass] = None
    license_expiry: Optional[date] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


def driver_to_dict(d: Driver) -> dict:
    return {
        "id": d.id,
        "employee_id": d.employee_id,
        "full_name": d.full_name,
        "email": d.email,
        "phone": d.phone,
        "license_number": d.license_number,
        "license_class": d.license_class,
        "license_expiry": d.license_expiry,
        "date_of_birth": d.date_of_birth,
        "address": d.address,
        "emergency_contact_name": d.emergency_contact_name,
        "emergency_contact_phone": d.emergency_contact_phone,
        "avatar_url": d.avatar_url,
        "total_trips": d.total_trips,
        "total_distance_km": d.total_distance_km,
        "average_risk_score": d.average_risk_score,
        "total_incidents": d.total_incidents,
        "safety_rating": d.safety_rating,
        "is_active": d.is_active,
        "notes": d.notes,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
    }


@router.get("/")
async def list_drivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Driver)
    if search:
        query = query.where(
            Driver.full_name.ilike(f"%{search}%") |
            Driver.employee_id.ilike(f"%{search}%") |
            Driver.email.ilike(f"%{search}%")
        )
    if is_active is not None:
        query = query.where(Driver.is_active == is_active)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    result = await db.execute(query.offset(skip).limit(limit).order_by(Driver.created_at.desc()))
    drivers = result.scalars().all()
    return {"total": total, "drivers": [driver_to_dict(d) for d in drivers]}


@router.post("/", status_code=201)
async def create_driver(
    data: DriverCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Driver).where(Driver.employee_id == data.employee_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    driver = Driver(**data.model_dump())
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver_to_dict(driver)


@router.get("/{driver_id}")
async def get_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver_to_dict(driver)


@router.patch("/{driver_id}")
async def update_driver(
    driver_id: int,
    data: DriverUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(driver, field, value)

    await db.commit()
    await db.refresh(driver)
    return driver_to_dict(driver)


@router.delete("/{driver_id}", status_code=204)
async def delete_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    await db.delete(driver)
    await db.commit()
