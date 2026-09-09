FROM python:3.11-slim

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working dir ───────────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps (cached layer) ────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Source code ───────────────────────────────────────────────────────────────
COPY . .

# ── Download YOLOv8n model if not present ────────────────────────────────────
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" || true

# ── Create directories ────────────────────────────────────────────────────────
RUN mkdir -p captures reports logs models

# ── Non-root user ─────────────────────────────────────────────────────────────
RUN useradd -m -u 1000 driveguard && chown -R driveguard:driveguard /app
USER driveguard

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

EXPOSE 8000

# ── Start ────────────────────────────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--loop", "asyncio", "--timeout-keep-alive", "75"]
