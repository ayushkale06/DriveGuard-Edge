import time


class Analytics:

    def __init__(self):

        self.start = time.time()

        self.timestamps = []
        self.risk_scores = []

        self.blinks = []
        self.yawns = []

        self.phone = []
        self.drowsy = []

        self.driver_states = []

    # -------------------------------------

    def update(self, info):

        t = time.time() - self.start

        self.timestamps.append(round(t, 1))

        self.risk_scores.append(info["risk_score"])

        self.blinks.append(info["blinks"])

        self.yawns.append(info["yawns"])

        self.phone.append(
            1 if info["phone"] == "PHONE DETECTED" else 0
        )

        self.drowsy.append(
            1 if info["driver"] == "DROWSY" else 0
        )

        self.driver_states.append(info["driver"])