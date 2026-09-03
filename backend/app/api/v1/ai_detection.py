"""
AI Detection WebSocket + HTTP endpoints.
Handles real-time frame processing from the browser camera.
"""

import base64
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2

from app.core.security import get_current_user
from app.models.user import User
from app.services.ai_engine import AIEngine

logger = logging.getLogger("driveguard.ai")
router = APIRouter()

# Single shared AI engine instance (thread-safe)
_ai_engine: Optional[AIEngine] = None


def get_ai_engine() -> AIEngine:
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine


@router.websocket("/ws/stream")
async def ai_stream_ws(websocket: WebSocket):
    """
    WebSocket endpoint for real-time AI processing.
    Client sends base64-encoded frames, receives JSON analysis results.
    """
    await websocket.accept()
    engine = get_ai_engine()
    logger.info("AI WebSocket connection opened")

    try:
        while True:
            data = await websocket.receive_json()
            frame_b64 = data.get("frame")
            if not frame_b64:
                continue

            # Decode base64 frame
            try:
                frame_bytes = base64.b64decode(frame_b64)
                np_arr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                    continue
            except Exception as e:
                logger.warning(f"Frame decode error: {e}")
                continue

            # Process frame
            result = await asyncio.get_event_loop().run_in_executor(
                None, engine.process_frame, frame
            )

            # Encode annotated frame back to base64
            _, buffer = cv2.imencode(".jpg", result["annotated_frame"],
                                     [cv2.IMWRITE_JPEG_QUALITY, 75])
            annotated_b64 = base64.b64encode(buffer).decode("utf-8")

            await websocket.send_json({
                "frame": annotated_b64,
                "data": result["data"]
            })

    except WebSocketDisconnect:
        logger.info("AI WebSocket disconnected")
    except Exception as e:
        logger.error(f"AI WebSocket error: {e}")


@router.post("/analyze-frame")
async def analyze_frame(request: dict):
    """
    HTTP endpoint for single frame analysis.
    Accepts base64 frame, returns analysis JSON.
    """
    frame_b64 = request.get("frame")
    if not frame_b64:
        raise HTTPException(status_code=400, detail="No frame provided")

    try:
        frame_bytes = base64.b64decode(frame_b64)
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Frame decode error: {e}")

    engine = get_ai_engine()
    result = await asyncio.get_event_loop().run_in_executor(
        None, engine.process_frame, frame
    )

    _, buffer = cv2.imencode(".jpg", result["annotated_frame"],
                             [cv2.IMWRITE_JPEG_QUALITY, 80])
    annotated_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "frame": annotated_b64,
        "data": result["data"]
    }


@router.get("/status")
async def ai_status():
    """Check AI engine status."""
    engine = get_ai_engine()
    return {
        "status": "ready",
        "modules": {
            "face_detection": True,
            "face_mesh": True,
            "eye_tracking": True,
            "blink_detection": True,
            "drowsiness": True,
            "head_pose": True,
            "yawn_detection": True,
            "phone_detection": engine.phone_detector_available,
            "seatbelt_detection": engine.seatbelt_detector_available,
        },
        "frame_count": engine.frame_count,
        "gpu_enabled": engine.gpu_enabled,
    }
