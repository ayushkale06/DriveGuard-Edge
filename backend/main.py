"""
DriveGuard Edge - FastAPI Backend
AI Powered Driver Monitoring & Road Safety Platform
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, drivers, vehicles, trips, incidents, analytics, ai_detection, reports, fleet, users

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("driveguard")


async def create_default_admin():
    """Create default admin user on first startup."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.core.security import hash_password
    from app.models.user import User, UserRole
    from app.models.driver import Driver
    from app.models.vehicle import Vehicle

    async with AsyncSessionLocal() as db:
        # Admin user
        result = await db.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@driveguard.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=hash_password("admin123"),
                role=UserRole.super_admin,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            logger.info("✅ Default admin created: admin / admin123")

        # Fleet manager
        result2 = await db.execute(select(User).where(User.username == "fleet"))
        if not result2.scalar_one_or_none():
            manager = User(
                email="fleet@driveguard.com",
                username="fleet",
                full_name="Fleet Manager",
                hashed_password=hash_password("fleet123"),
                role=UserRole.fleet_manager,
                is_active=True,
                is_verified=True,
            )
            db.add(manager)

        # Sample drivers
        for emp_id, name, email, phone in [
            ("EMP-001", "Alice Johnson",  "alice@driveguard.com",  "+1-555-0101"),
            ("EMP-002", "Bob Williams",   "bob@driveguard.com",    "+1-555-0102"),
            ("EMP-003", "Carlos Mendez",  "carlos@driveguard.com", "+1-555-0103"),
        ]:
            ex = await db.execute(select(Driver).where(Driver.employee_id == emp_id))
            if not ex.scalar_one_or_none():
                db.add(Driver(employee_id=emp_id, full_name=name, email=email, phone=phone))

        # Sample vehicles
        for plate, make, model, year, color in [
            ("DG-001", "Toyota", "Camry",   2022, "White"),
            ("DG-002", "Ford",   "Transit", 2021, "Silver"),
            ("DG-003", "Honda",  "CR-V",    2023, "Black"),
        ]:
            ex = await db.execute(select(Vehicle).where(Vehicle.plate_number == plate))
            if not ex.scalar_one_or_none():
                db.add(Vehicle(plate_number=plate, make=make, model=model, year=year, color=color))

        await db.commit()


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚗 DriveGuard Edge Backend starting...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables ready")

    for d in ["captures", "reports", "logs", "models"]:
        os.makedirs(d, exist_ok=True)

    await create_default_admin()
    logger.info("✅ DriveGuard Edge is ready — docs at /api/docs")
    yield
    logger.info("🛑 DriveGuard Edge shutting down...")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DriveGuard Edge API",
    description="AI Powered Driver Monitoring & Road Safety Platform — v2.0",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ─── Prometheus metrics ───────────────────────────────────────────────────────
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except ImportError:
    pass

# ─── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ─── Static Files ─────────────────────────────────────────────────────────────
os.makedirs("captures", exist_ok=True)
os.makedirs("reports",  exist_ok=True)
app.mount("/captures", StaticFiles(directory="captures"), name="captures")
app.mount("/reports",  StaticFiles(directory="reports"),  name="reports")

# ─── Routers ──────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth.router,         prefix=f"{PREFIX}/auth",       tags=["Authentication"])
app.include_router(users.router,        prefix=f"{PREFIX}/users",      tags=["Users"])
app.include_router(drivers.router,      prefix=f"{PREFIX}/drivers",    tags=["Drivers"])
app.include_router(vehicles.router,     prefix=f"{PREFIX}/vehicles",   tags=["Vehicles"])
app.include_router(trips.router,        prefix=f"{PREFIX}/trips",      tags=["Trips"])
app.include_router(incidents.router,    prefix=f"{PREFIX}/incidents",  tags=["Incidents"])
app.include_router(analytics.router,    prefix=f"{PREFIX}/analytics",  tags=["Analytics"])
app.include_router(ai_detection.router, prefix=f"{PREFIX}/ai",         tags=["AI Detection"])
app.include_router(reports.router,      prefix=f"{PREFIX}/reports",    tags=["Reports"])
app.include_router(fleet.router,        prefix=f"{PREFIX}/fleet",      tags=["Fleet"])

# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "DriveGuard Edge API", "version": "2.0.0"}

@app.get("/", tags=["Root"])
async def root():
    return {"message": "DriveGuard Edge API", "docs": "/api/docs", "health": "/health"}
