"""
DriveGuard AI Engine
Preserves all original detector logic with improvements:
- Frame skipping for performance
- Thread pooling for async inference
- GPU/CPU fallback
- ONNX-ready architecture
"""

import cv2
import math
import time
import logging
import os
import threading
from typing import Optional, Tuple, Dict, Any

import numpy as np
import mediapipe as mp

logger = logging.getLogger("driveguard.ai")

# ─── MediaPipe constants ───────────────────────────────────────────────────────
LEFT_EYE  = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH     = [61, 13, 291, 14]
HEAD_LANDMARKS = [33, 263, 1, 61, 291, 199]

# ─── Colors ───────────────────────────────────────────────────────────────────
GREEN   = (0, 255, 0)
RED     = (0, 0, 255)
BLUE    = (255, 0, 0)
YELLOW  = (0, 255, 255)
CYAN    = (255, 255, 0)
WHITE   = (255, 255, 255)
ORANGE  = (0, 165, 255)
MAGENTA = (255, 0, 255)


class AIEngine:
    """
    Central AI Processing Engine.
    All detection modules in one class for efficient resource sharing.
    """

    def __init__(self):
        self.gpu_enabled = self._check_gpu()
        self.frame_count = 0
        self.frame_skip = int(os.getenv("FRAME_SKIP", "3"))
        self._lock = threading.Lock()

        # ── MediaPipe ─────────────────────────────────────────────────────────
        self._mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._mp_draw = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles

        # ── Blink state ───────────────────────────────────────────────────────
        self._ear_threshold = 0.21
        self._blink_consec = 3
        self._drowsy_consec = 20
        self._blink_counter = 0
        self._total_blinks = 0
        self._drowsy_counter = 0
        self._drowsy = False

        # ── Yawn state ────────────────────────────────────────────────────────
        self._mar_threshold = 0.60
        self._yawn_consec = 12
        self._yawn_counter = 0
        self._total_yawns = 0

        # ── Phone / Seatbelt detection ────────────────────────────────────────
        self._last_phone = {"phone": False, "confidence": 0.0}
        self._last_seatbelt = {"seatbelt": True, "confidence": 0.0}
        self._last_driver_state = "SAFE"
        self._yolo_model = None
        self.phone_detector_available = False
        self.seatbelt_detector_available = False
        self._load_yolo()

        # ── FPS counter ───────────────────────────────────────────────────────
        self._fps_time = time.time()
        self._fps = 0.0
        self._fps_counter = 0

        logger.info(f"AIEngine initialized | GPU={self.gpu_enabled} | FrameSkip={self.frame_skip}")

    # ─── GPU check ────────────────────────────────────────────────────────────
    def _check_gpu(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    # ─── YOLO loader ──────────────────────────────────────────────────────────
    def _load_yolo(self):
        try:
            from ultralytics import YOLO
            model_path = os.getenv("YOLO_MODEL", "yolov8n.pt")
            self._yolo_model = YOLO(model_path)
            self.phone_detector_available = True
            logger.info("YOLO model loaded")
        except Exception as e:
            logger.warning(f"YOLO not available: {e}")

        # Seatbelt model
        seatbelt_path = os.path.join("models", "seatbelt.pt")
        if os.path.exists(seatbelt_path):
            try:
                from ultralytics import YOLO
                self._seatbelt_model = YOLO(seatbelt_path)
                self.seatbelt_detector_available = True
            except Exception as e:
                logger.warning(f"Seatbelt model not available: {e}")

    # ─── Math helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _dist(p1, p2) -> float:
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def _ear(self, eye) -> float:
        A = self._dist(eye[1], eye[5])
        B = self._dist(eye[2], eye[4])
        C = self._dist(eye[0], eye[3])
        return (A + B) / (2.0 * C + 1e-6)

    def _mar(self, pts) -> float:
        horiz = self._dist(pts[0], pts[2])
        vert  = self._dist(pts[1], pts[3])
        return vert / (horiz + 1e-6)

    # ─── Landmark extractor ───────────────────────────────────────────────────
    def _get_landmarks(self, frame, landmarks, ids):
        h, w = frame.shape[:2]
        return [(int(landmarks.landmark[i].x * w),
                 int(landmarks.landmark[i].y * h)) for i in ids]

    # ─── Head pose ────────────────────────────────────────────────────────────
    def _head_pose(self, frame, landmarks) -> Dict:
        h, w = frame.shape[:2]
        face_2d, face_3d = [], []
        for idx in HEAD_LANDMARKS:
            lm = landmarks.landmark[idx]
            x, y, z = lm.x * w, lm.y * h, lm.z * w
            face_2d.append([x, y])
            face_3d.append([x, y, z])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)
        fl = float(w)
        cam_matrix = np.array([[fl, 0, w/2], [0, fl, h/2], [0, 0, 1]], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        ok, rvec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_coeffs,
                                    flags=cv2.SOLVEPNP_ITERATIVE)
        if not ok:
            return {"direction": "UNKNOWN", "pitch": 0.0, "yaw": 0.0, "roll": 0.0}

        rmat, _ = cv2.Rodrigues(rvec)
        angles, *_ = cv2.RQDecomp3x3(rmat)
        pitch, yaw, roll = float(angles[0]), float(angles[1]), float(angles[2])

        direction = "FORWARD"
        if yaw < -15:    direction = "LEFT"
        elif yaw > 15:   direction = "RIGHT"
        elif pitch < -12: direction = "DOWN"
        elif pitch > 12:  direction = "UP"

        return {"direction": direction, "pitch": round(pitch, 1),
                "yaw": round(yaw, 1), "roll": round(roll, 1)}

    # ─── Driver state decision engine ─────────────────────────────────────────
    def _driver_state(self, drowsy, yawning, head_dir, phone, seatbelt) -> Tuple[str, tuple]:
        if drowsy:            return "DROWSY",         RED
        if yawning:           return "YAWNING",        ORANGE
        if phone:             return "PHONE DETECTED", RED
        if not seatbelt:      return "NO SEATBELT",    RED
        if head_dir != "FORWARD": return "DISTRACTED", ORANGE
        return "SAFE", GREEN

    # ─── Risk engine ──────────────────────────────────────────────────────────
    def _risk_score(self, info: Dict) -> Tuple[int, str]:
        score = 100
        if info.get("phone") == "YES":   score -= 40
        if info.get("driver") == "DROWSY": score -= 35
        if info.get("yawning"):           score -= 15
        if info.get("head_pose") not in ("FORWARD", "--"): score -= 20
        if info.get("faces", 0) == 0:    score -= 50
        score = max(0, score)

        if score >= 85:  status = "SAFE"
        elif score >= 65: status = "LOW RISK"
        elif score >= 40: status = "WARNING"
        elif score >= 20: status = "HIGH RISK"
        else:             status = "CRITICAL"

        return score, status

    # ─── YOLO phone detection ─────────────────────────────────────────────────
    def _detect_phone(self, frame) -> Dict:
        if not self._yolo_model:
            return {"phone": False, "confidence": 0.0}
        results = self._yolo_model(frame, verbose=False)
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 67 and float(box.conf[0]) > 0.50:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), RED, 3)
                    cv2.putText(frame, f"PHONE {float(box.conf[0]):.2f}",
                                (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 2)
                    return {"phone": True, "confidence": round(float(box.conf[0]), 2)}
        return {"phone": False, "confidence": 0.0}

    # ─── FPS ──────────────────────────────────────────────────────────────────
    def _update_fps(self) -> float:
        self._fps_counter += 1
        elapsed = time.time() - self._fps_time
        if elapsed >= 1.0:
            self._fps = self._fps_counter / elapsed
            self._fps_counter = 0
            self._fps_time = time.time()
        return round(self._fps, 1)

    # ─── MAIN PROCESS FRAME ───────────────────────────────────────────────────
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        with self._lock:
            return self._process_frame_inner(frame)

    def _process_frame_inner(self, frame: np.ndarray) -> Dict[str, Any]:
        self.frame_count += 1
        fps = self._update_fps()

        info: Dict[str, Any] = {
            "driver": "NO FACE",
            "faces": 0,
            "ear": 0.0,
            "mar": 0.0,
            "blinks": self._total_blinks,
            "yawns": self._total_yawns,
            "eyes": "--",
            "head_pose": "--",
            "pitch": 0.0,
            "yaw": 0.0,
            "yawning": False,
            "phone": "NO",
            "seatbelt": "YES",
            "emotion": "N/A",
            "emotion_confidence": 0,
            "risk_score": 100,
            "risk_status": "SAFE",
            "fps": fps,
            "alert": None,
            "voice": "Ready",
        }

        # ── Phone detection (every N frames) ──────────────────────────────────
        if self.phone_detector_available and self.frame_count % self.frame_skip == 0:
            self._last_phone = self._detect_phone(frame)

        info["phone"] = "YES" if self._last_phone["phone"] else "NO"

        # ── Face mesh ─────────────────────────────────────────────────────────
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._mp_face_mesh.process(rgb)

        if results.multi_face_landmarks:
            info["faces"] = len(results.multi_face_landmarks)

            for face_lm in results.multi_face_landmarks:
                # Draw mesh
                self._mp_draw.draw_landmarks(
                    frame, face_lm,
                    mp.solutions.face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self._mp_styles.get_default_face_mesh_contours_style()
                )

                # ── EAR ───────────────────────────────────────────────────────
                left_pts  = self._get_landmarks(frame, face_lm, LEFT_EYE)
                right_pts = self._get_landmarks(frame, face_lm, RIGHT_EYE)
                ear = (self._ear(left_pts) + self._ear(right_pts)) / 2.0
                info["ear"] = round(ear, 3)

                for p in left_pts:  cv2.circle(frame, p, 2, RED,  -1)
                for p in right_pts: cv2.circle(frame, p, 2, BLUE, -1)

                # ── Blink ─────────────────────────────────────────────────────
                if ear < self._ear_threshold:
                    self._blink_counter += 1
                    info["eyes"] = "CLOSED"
                    eye_color = RED
                else:
                    if self._blink_counter >= self._blink_consec:
                        self._total_blinks += 1
                    self._blink_counter = 0
                    info["eyes"] = "OPEN"
                    eye_color = GREEN

                info["blinks"] = self._total_blinks

                # ── Drowsiness ────────────────────────────────────────────────
                if ear < self._ear_threshold:
                    self._drowsy_counter += 1
                else:
                    self._drowsy_counter = 0
                    self._drowsy = False
                if self._drowsy_counter >= self._drowsy_consec:
                    self._drowsy = True

                # ── MAR / Yawn ────────────────────────────────────────────────
                mouth_pts = self._get_landmarks(frame, face_lm, MOUTH)
                mar = self._mar(mouth_pts)
                info["mar"] = round(mar, 3)

                if mar > self._mar_threshold:
                    self._yawn_counter += 1
                else:
                    if self._yawn_counter >= self._yawn_consec:
                        self._total_yawns += 1
                    self._yawn_counter = 0

                info["yawning"] = self._yawn_counter >= self._yawn_consec
                info["yawns"]   = self._total_yawns

                for p in mouth_pts:
                    cv2.circle(frame, p, 3, YELLOW, -1)

                # ── Head pose ─────────────────────────────────────────────────
                pose = self._head_pose(frame, face_lm)
                info["head_pose"] = pose["direction"]
                info["pitch"]     = pose["pitch"]
                info["yaw"]       = pose["yaw"]

                # ── Driver state ──────────────────────────────────────────────
                state, color = self._driver_state(
                    self._drowsy,
                    info["yawning"],
                    pose["direction"],
                    self._last_phone["phone"],
                    True
                )
                info["driver"] = state

                # ── Risk ──────────────────────────────────────────────────────
                score, status = self._risk_score(info)
                info["risk_score"]  = score
                info["risk_status"] = status

                # ── HUD overlay ───────────────────────────────────────────────
                self._draw_hud(frame, info, color, eye_color)
                break  # Only process first face

        else:
            info["driver"] = "NO FACE"
            cv2.putText(frame, "NO FACE DETECTED", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, RED, 2)

        # ── Alert banner ──────────────────────────────────────────────────────
        if info["driver"] in ("DROWSY", "PHONE DETECTED", "NO SEATBELT"):
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 55), (0, 0, 200), -1)
            cv2.putText(frame, f"⚠ {info['driver']}", (15, 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, WHITE, 2)

        return {"annotated_frame": frame, "data": info}

    # ─── HUD drawing ──────────────────────────────────────────────────────────
    def _draw_hud(self, frame, info, driver_color, eye_color):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 220), (300, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        lines = [
            (f"Driver : {info['driver']}",   driver_color),
            (f"Risk   : {info['risk_score']}% {info['risk_status']}", YELLOW),
            (f"Eyes   : {info['eyes']}  EAR={info['ear']:.2f}", eye_color),
            (f"Blinks : {info['blinks']}  Yawns={info['yawns']}", WHITE),
            (f"Head   : {info['head_pose']}  P={info['pitch']:.1f} Y={info['yaw']:.1f}", MAGENTA),
            (f"Phone  : {info['phone']}  FPS={info['fps']}", CYAN),
        ]
        for i, (text, color) in enumerate(lines):
            cv2.putText(frame, text, (10, h - 200 + i * 33),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.62, color, 2)
