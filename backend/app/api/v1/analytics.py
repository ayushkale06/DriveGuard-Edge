from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.trip import Trip, TripStatus
from app.models.incident import Incident
from app.models.analytics import AnalyticsSnapshot

router = APIRouter()


@router.get("/dashboard")
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fleet-wide dashboard summary."""
    total_drivers = (await db.execute(select(func.count(Driver.id)))).scalar()
    active_drivers = (await db.execute(select(func.count(Driver.id)).where(Driver.is_active == True))).scalar()
    total_vehicles = (await db.execute(select(func.count(Vehicle.id)))).scalar()
    total_trips = (await db.execute(select(func.count(Trip.id)))).scalar()
    active_trips = (await db.execute(select(func.count(Trip.id)).where(Trip.status == TripStatus.active))).scalar()
    total_incidents = (await db.execute(select(func.count(Incident.id)))).scalar()

    # Average risk from last 100 trips
    avg_risk = (await db.execute(
        select(func.avg(Trip.average_risk_score))
        .where(Trip.status == TripStatus.completed)
        .limit(100)
    )).scalar() or 100.0

    # Today's trips
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_trips = (await db.execute(
        select(func.count(Trip.id)).where(Trip.start_time >= today)
    )).scalar()

    # Today's incidents
    today_incidents = (await db.execute(
        select(func.count(Incident.id)).where(Incident.occurred_at >= today)
    )).scalar()

    # Last 7 days trips per day
    result = await db.execute(
        select(
            func.date(Trip.start_time).label("date"),
            func.count(Trip.id).label("count")
        )
        .where(Trip.start_time >= datetime.utcnow() - timedelta(days=7))
        .group_by(func.date(Trip.start_time))
        .order_by(func.date(Trip.start_time))
    )
    trips_trend = [{"date": str(row.date), "trips": row.count} for row in result]

    # Incident type distribution
    inc_result = await db.execute(
        select(Incident.incident_type, func.count(Incident.id).label("count"))
        .group_by(Incident.incident_type)
    )
    incident_types = [{"type": row.incident_type, "count": row.count} for row in inc_result]

    return {
        "total_drivers": total_drivers,
        "active_drivers": active_drivers,
        "total_vehicles": total_vehicles,
        "total_trips": total_trips,
        "active_trips": active_trips,
        "today_trips": today_trips,
        "total_incidents": total_incidents,
        "today_incidents": today_incidents,
        "average_fleet_risk": round(avg_risk, 1),
        "trips_trend": trips_trend,
        "incident_types": incident_types,
    }


@router.get("/risk-timeline")
async def risk_timeline(
    driver_id: Optional[int] = Query(None),
    trip_id: Optional[int] = Query(None),
    hours: int = Query(1, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(AnalyticsSnapshot).where(
        AnalyticsSnapshot.timestamp >= datetime.utcnow() - timedelta(hours=hours)
    )
    if driver_id:
        query = query.where(AnalyticsSnapshot.driver_id == driver_id)
    if trip_id:
        query = query.where(AnalyticsSnapshot.trip_id == trip_id)

    result = await db.execute(query.order_by(AnalyticsSnapshot.timestamp.asc()).limit(1000))
    snapshots = result.scalars().all()

    return [
        {
            "timestamp": s.timestamp.isoformat(),
            "risk_score": s.risk_score,
            "ear": s.ear,
            "mar": s.mar,
            "blinks": s.blinks,
            "yawns": s.yawns,
            "driver_state": s.driver_state,
            "head_pose": s.head_pose,
            "emotion": s.emotion,
            "phone_detected": s.phone_detected,
        }
        for s in snapshots
    ]


@router.get("/driver/{driver_id}/summary")
async def driver_analytics_summary(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        return {"error": "Driver not found"}

    total_trips = (await db.execute(select(func.count(Trip.id)).where(Trip.driver_id == driver_id))).scalar()
    total_incidents = (await db.execute(select(func.count(Incident.id)).where(Incident.driver_id == driver_id))).scalar()
    avg_risk = (await db.execute(
        select(func.avg(Trip.average_risk_score)).where(Trip.driver_id == driver_id)
    )).scalar() or 100.0

    inc_result = await db.execute(
        select(Incident.incident_type, func.count(Incident.id).label("count"))
        .where(Incident.driver_id == driver_id)
        .group_by(Incident.incident_type)
    )
    incident_breakdown = {row.incident_type: row.count for row in inc_result}

    return {
        "driver_id": driver_id,
        "driver_name": driver.full_name,
        "total_trips": total_trips,
        "total_incidents": total_incidents,
        "average_risk_score": round(avg_risk, 1),
        "safety_rating": driver.safety_rating,
        "incident_breakdown": incident_breakdown,
    }
