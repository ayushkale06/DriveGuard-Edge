from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.trip import Trip, TripStatus
from app.models.incident import Incident

router = APIRouter()


@router.get("/overview")
async def fleet_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fleet management overview."""
    drivers = (await db.execute(select(func.count(Driver.id)))).scalar()
    active_drivers = (await db.execute(select(func.count(Driver.id)).where(Driver.is_active == True))).scalar()
    vehicles = (await db.execute(select(func.count(Vehicle.id)))).scalar()
    active_vehicles = (await db.execute(select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.active))).scalar()
    maintenance_vehicles = (await db.execute(select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.maintenance))).scalar()
    active_trips = (await db.execute(select(func.count(Trip.id)).where(Trip.status == TripStatus.active))).scalar()
    total_incidents = (await db.execute(select(func.count(Incident.id)))).scalar()

    return {
        "total_drivers": drivers,
        "active_drivers": active_drivers,
        "inactive_drivers": drivers - active_drivers,
        "total_vehicles": vehicles,
        "active_vehicles": active_vehicles,
        "maintenance_vehicles": maintenance_vehicles,
        "inactive_vehicles": vehicles - active_vehicles - maintenance_vehicles,
        "active_trips": active_trips,
        "total_incidents": total_incidents,
    }


@router.get("/live")
async def live_fleet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active trips with driver and vehicle details."""
    result = await db.execute(
        select(Trip, Driver, Vehicle)
        .join(Driver, Trip.driver_id == Driver.id)
        .outerjoin(Vehicle, Trip.vehicle_id == Vehicle.id)
        .where(Trip.status == TripStatus.active)
        .order_by(Trip.start_time.desc())
    )
    rows = result.all()

    return [
        {
            "trip_id": trip.id,
            "trip_code": trip.trip_code,
            "driver": {"id": driver.id, "name": driver.full_name, "employee_id": driver.employee_id},
            "vehicle": {"id": vehicle.id, "plate": vehicle.plate_number, "make": vehicle.make, "model": vehicle.model} if vehicle else None,
            "start_time": trip.start_time,
            "risk_score": trip.average_risk_score,
            "start_location": trip.start_location,
        }
        for trip, driver, vehicle in rows
    ]
