import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.analytics import Report

router = APIRouter()


@router.get("/")
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Report).order_by(Report.created_at.desc()).limit(50))
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "report_code": r.report_code,
            "title": r.title,
            "report_type": r.report_type,
            "file_path": r.file_path,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in reports
    ]


@router.post("/generate")
async def generate_report(
    request: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a PDF report for a trip or driver."""
    report_code = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    report = Report(
        report_code=report_code,
        title=request.get("title", "DriveGuard Report"),
        report_type=request.get("report_type", "trip"),
        driver_id=request.get("driver_id"),
        trip_id=request.get("trip_id"),
        status="pending",
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # In production, trigger async PDF generation task
    return {
        "report_code": report_code,
        "status": "pending",
        "message": "Report generation queued"
    }
