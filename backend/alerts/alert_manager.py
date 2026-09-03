"""
Alert manager — evaluates driver info and returns active alerts.
Used by the AI engine / frame processor.
"""


class AlertManager:

    def __init__(self):
        self.last_alert = None

    def get_alert(self, info: dict) -> dict | None:

        driver = info.get("driver", "")
        risk   = info.get("risk_status", "SAFE")

        if driver == "DROWSY":
            return {"type": "DROWSY",  "message": "⚠ DRIVER DROWSY — Wake up!", "severity": "critical"}

        if info.get("phone") == "YES":
            return {"type": "PHONE",   "message": "📱 PHONE DETECTED — Put it down!", "severity": "high"}

        if driver == "NO SEATBELT":
            return {"type": "SEATBELT","message": "🪑 NO SEATBELT — Buckle up!", "severity": "high"}

        if driver == "YAWNING":
            return {"type": "YAWN",    "message": "😴 YAWNING — Consider a break", "severity": "medium"}

        if driver == "DISTRACTED":
            return {"type": "DISTRACT","message": "👀 DISTRACTED — Eyes on road!", "severity": "medium"}

        if risk == "CRITICAL":
            return {"type": "CRITICAL","message": "🚨 CRITICAL RISK DETECTED!",    "severity": "critical"}

        return None
