import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.incident import Incident, Alert, IncidentType, IncidentSeverity

router = APIRouter()


class IncidentCreate(BaseModel):
    driver_id: int
    trip_id: Optional[int] = None
    incident_type: IncidentType
    severity: Optional[IncidentSeverity] = IncidentSeverity.medium
    description: Optional[str] = None
    risk_score_at_time: Optional[float] = None
    ear_value: Optional[float] = None
    mar_value: Optional[float] = None
    head_pose: Optional[str] = None
    emotion: Optional[str] = None
    screenshot_path: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None


def incident_to_dict(i: Incident) -> dict:
    return {
        "id": i.id,
        "incident_code": i.incident_code,
        "trip_id": i.trip_id,
        "driver_id": i.driver_id,
        "incident_type": i.incident_type,
        "severity": i.severity,
        "description": i.description,
        "risk_score_at_time": i.risk_score_at_time,
        "ear_value": i.ear_value,
        "mar_value": i.mar_value,
        "head_pose": i.head_pose,
        "emotion": i.emotion,
        "screenshot_path": i.screenshot_path,
        "latitude": i.latitude,
        "longitude": i.longitude,
        "location_name": i.location_name,
        "acknowledged": i.acknowledged,
        "occurred_at": i.occurred_at,
        "created_at": i.created_at,
    }


@router.get("/")
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    driver_id: Optional[int] = Query(None),
    trip_id: Optional[int] = Query(None),
    incident_type: Optional[IncidentType] = Query(None),
    severity: Optional[IncidentSeverity] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Incident)
    if driver_id:
        query = query.where(Incident.driver_id == driver_id)
    if trip_id:
        query = query.where(Incident.trip_id == trip_id)
    if incident_type:
        query = query.where(Incident.incident_type == incident_type)
    if severity:
        query = query.where(Incident.severity == severity)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    result = await db.execute(query.offset(skip).limit(limit).order_by(Incident.occurred_at.desc()))
    incidents = result.scalars().all()
    return {"total": total, "incidents": [incident_to_dict(i) for i in incidents]}


@router.post("/", status_code=201)
async def create_incident(
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident_code = f"INC-{uuid.uuid4().hex[:8].upper()}"
    incident = Incident(
        incident_code=incident_code,
        **data.model_dump()
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident_to_dict(incident)


@router.get("/stats")
async def incident_stats(
    driver_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Incident.incident_type, func.count(Incident.id).label("count"))
    if driver_id:
        query = query.where(Incident.driver_id == driver_id)
    query = query.group_by(Incident.incident_type)
    result = await db.execute(query)
    rows = result.all()
    return {row.incident_type: row.count for row in rows}


@router.get("/{incident_id}")
async def get_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident_to_dict(incident)


@router.post("/{incident_id}/acknowledge")
async def acknowledge_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.acknowledged = True
    incident.acknowledged_by = current_user.id
    incident.acknowledged_at = datetime.utcnow()
    await db.commit()
    return {"message": "Incident acknowledged"}


# ─── Alerts ───────────────────────────────────────────────────────────────────
@router.get("/alerts/unread")
async def get_unread_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Alert).where(Alert.is_read == False).order_by(Alert.created_at.desc()).limit(50)
    )
    alerts = result.scalars().all()
    return [{"id": a.id, "alert_type": a.alert_type, "message": a.message,
             "severity": a.severity, "created_at": a.created_at} for a in alerts]
