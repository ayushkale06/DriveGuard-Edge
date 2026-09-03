-- DriveGuard Edge — PostgreSQL init script
-- Creates the database (already created by POSTGRES_DB env var)
-- This file runs on first container startup

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for fast text search

-- Seed default admin user (password: admin123)
-- This will be inserted by the FastAPI startup seed script
