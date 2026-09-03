import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.trip import Trip, TripStatus

router = APIRouter()


class TripCreate(BaseModel):
    driver_id: int
    vehicle_id: Optional[int] = None
    start_location: Optional[str] = None
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None


class TripUpdate(BaseModel):
    status: Optional[TripStatus] = None
    end_location: Optional[str] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    distance_km: Optional[float] = None
    average_risk_score: Optional[float] = None
    safety_score: Optional[float] = None
    total_blinks: Optional[int] = None
    total_yawns: Optional[int] = None
    drowsy_events: Optional[int] = None
    phone_events: Optional[int] = None
    distraction_events: Optional[int] = None
    notes: Optional[str] = None


def trip_to_dict(t: Trip) -> dict:
    return {
        "id": t.id,
        "trip_code": t.trip_code,
        "driver_id": t.driver_id,
        "vehicle_id": t.vehicle_id,
        "status": t.status,
        "start_time": t.start_time,
        "end_time": t.end_time,
        "duration_seconds": t.duration_seconds,
        "distance_km": t.distance_km,
        "start_location": t.start_location,
        "end_location": t.end_location,
        "average_risk_score": t.average_risk_score,
        "min_risk_score": t.min_risk_score,
        "max_risk_score": t.max_risk_score,
        "total_blinks": t.total_blinks,
        "total_yawns": t.total_yawns,
        "drowsy_events": t.drowsy_events,
        "phone_events": t.phone_events,
        "distraction_events": t.distraction_events,
        "no_seatbelt_events": t.no_seatbelt_events,
        "critical_alerts": t.critical_alerts,
        "safety_score": t.safety_score,
        "frames_processed": t.frames_processed,
        "notes": t.notes,
        "created_at": t.created_at,
    }


@router.get("/")
async def list_trips(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    driver_id: Optional[int] = Query(None),
    status: Optional[TripStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Trip)
    if driver_id:
        query = query.where(Trip.driver_id == driver_id)
    if status:
        query = query.where(Trip.status == status)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    result = await db.execute(query.offset(skip).limit(limit).order_by(Trip.start_time.desc()))
    trips = result.scalars().all()
    return {"total": total, "trips": [trip_to_dict(t) for t in trips]}


@router.post("/", status_code=201)
async def start_trip(
    data: TripCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trip_code = f"TRP-{uuid.uuid4().hex[:8].upper()}"
    trip = Trip(
        trip_code=trip_code,
        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id,
        start_location=data.start_location,
        start_lat=data.start_lat,
        start_lng=data.start_lng,
        status=TripStatus.active,
        start_time=datetime.utcnow()
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip_to_dict(trip)


@router.get("/active")
async def get_active_trips(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Trip).where(Trip.status == TripStatus.active).order_by(Trip.start_time.desc())
    )
    trips = result.scalars().all()
    return [trip_to_dict(t) for t in trips]


@router.get("/{trip_id}")
async def get_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip_to_dict(trip)


@router.patch("/{trip_id}")
async def update_trip(
    trip_id: int,
    data: TripUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(trip, field, value)

    if data.status == TripStatus.completed and not trip.end_time:
        trip.end_time = datetime.utcnow()
        if trip.start_time:
            trip.duration_seconds = int((trip.end_time - trip.start_time).total_seconds())

    await db.commit()
    await db.refresh(trip)
    return trip_to_dict(trip)


@router.post("/{trip_id}/end")
async def end_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip.status = TripStatus.completed
    trip.end_time = datetime.utcnow()
    if trip.start_time:
        trip.duration_seconds = int((trip.end_time - trip.start_time).total_seconds())

    await db.commit()
    await db.refresh(trip)
    return trip_to_dict(trip)
