import time


class DashboardData:

    def __init__(self):

        self.start_time = time.time()

        self.total_blinks = 0
        self.total_yawns = 0

        self.phone_events = 0
        self.drowsy_events = 0
        self.distraction_events = 0

        self.last_blink = 0
        self.last_yawn = 0

        self.phone_active = False
        self.drowsy_active = False
        self.distraction_active = False

    # ----------------------------------------

    def update(self, info):

        # -------------------------------
        # Blink Counter
        # -------------------------------

        if info["blinks"] > self.last_blink:

            self.total_blinks = info["blinks"]

            self.last_blink = info["blinks"]

        # -------------------------------
        # Yawn Counter
        # -------------------------------

        if info["yawns"] > self.last_yawn:

            self.total_yawns = info["yawns"]

            self.last_yawn = info["yawns"]

        # -------------------------------
        # Phone Events
        # -------------------------------

        if info["phone"] == "PHONE DETECTED":

            if not self.phone_active:

                self.phone_events += 1

                self.phone_active = True

        else:

            self.phone_active = False

        # -------------------------------
        # Drowsiness Events
        # -------------------------------

        if info["driver"] == "DROWSY":

            if not self.drowsy_active:

                self.drowsy_events += 1

                self.drowsy_active = True

        else:

            self.drowsy_active = False

        # -------------------------------
        # Distraction Events
        # -------------------------------

        if info["driver"] == "DISTRACTED":

            if not self.distraction_active:

                self.distraction_events += 1

                self.distraction_active = True

        else:

            self.distraction_active = False

    # ----------------------------------------

    def trip_time(self):

        return int(time.time() - self.start_time)