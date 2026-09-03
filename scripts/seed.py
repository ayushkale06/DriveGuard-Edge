#!/usr/bin/env python3
"""
Seed script — creates default admin user and sample data.
Run: python scripts/seed.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.driver import Driver
from app.models.vehicle import Vehicle

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSession_ = async_sessionmaker(engine, expire_on_commit=False)


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession_() as db:
        # ── Admin user ────────────────────────────────────────────────
        existing = await db.execute(select(User).where(User.username == 'admin'))
        if not existing.scalar_one_or_none():
            admin = User(
                email='admin@driveguard.com',
                username='admin',
                full_name='System Administrator',
                hashed_password=hash_password('admin123'),
                role=UserRole.super_admin,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            print("✅ Created admin user  (admin / admin123)")

        # ── Fleet manager ─────────────────────────────────────────────
        existing2 = await db.execute(select(User).where(User.username == 'fleet'))
        if not existing2.scalar_one_or_none():
            manager = User(
                email='fleet@driveguard.com',
                username='fleet',
                full_name='Fleet Manager',
                hashed_password=hash_password('fleet123'),
                role=UserRole.fleet_manager,
                is_active=True,
                is_verified=True,
            )
            db.add(manager)
            print("✅ Created fleet manager (fleet / fleet123)")

        # ── Sample drivers ────────────────────────────────────────────
        sample_drivers = [
            ('EMP-001', 'Alice Johnson',  'alice@driveguard.com',  '+1-555-0101'),
            ('EMP-002', 'Bob Williams',   'bob@driveguard.com',    '+1-555-0102'),
            ('EMP-003', 'Carlos Mendez',  'carlos@driveguard.com', '+1-555-0103'),
            ('EMP-004', 'Diana Park',     'diana@driveguard.com',  '+1-555-0104'),
        ]
        for emp_id, name, email, phone in sample_drivers:
            ex = await db.execute(select(Driver).where(Driver.employee_id == emp_id))
            if not ex.scalar_one_or_none():
                db.add(Driver(employee_id=emp_id, full_name=name, email=email, phone=phone))
                print(f"✅ Created driver {name}")

        # ── Sample vehicles ───────────────────────────────────────────
        sample_vehicles = [
            ('DG-001', 'Toyota', 'Camry',   2022, 'White'),
            ('DG-002', 'Ford',   'Transit', 2021, 'Silver'),
            ('DG-003', 'Honda',  'CR-V',    2023, 'Black'),
        ]
        for plate, make, model, year, color in sample_vehicles:
            ex = await db.execute(select(Vehicle).where(Vehicle.plate_number == plate))
            if not ex.scalar_one_or_none():
                db.add(Vehicle(plate_number=plate, make=make, model=model, year=year, color=color))
                print(f"✅ Created vehicle {plate}")

        await db.commit()
        print("\n🚗 DriveGuard Edge seed complete!")


if __name__ == '__main__':
    asyncio.run(seed())
