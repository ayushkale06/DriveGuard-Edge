import threading


class SharedState:

    def __init__(self):

        self.lock = threading.Lock()

        self.info = {
            "driver": "Unknown",
            "faces": 0,
            "ear": 0.0,
            "blinks": 0,
            "eyes": "--",
            "seatbelt": "--",
            "phone": "--",
            "emotion": "--",
            "risk_score": 100,
            "risk_status": "SAFE",
            "fps": 0,
            "yawns": 0,
            "head_pose": "--",
            "alert": None
        }

    def update(self, info):
        with self.lock:
            self.info = info.copy()

    def get(self):
        with self.lock:
            return self.info.copy()


shared_state = SharedState()