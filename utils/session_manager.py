import time


class SessionManager:

    def __init__(self):

        self.active = False
        self.paused = False
        self.start_time = None

    # -----------------------------

    def start(self):

        self.active = True
        self.paused = False
        self.start_time = time.time()

    # -----------------------------

    def pause(self):

        self.paused = True

    # -----------------------------

    def resume(self):

        self.paused = False

    # -----------------------------

    def stop(self):

        self.active = False
        self.paused = False

    # -----------------------------

    def running(self):

        return self.active and not self.paused

    # -----------------------------

    def duration(self):

        if self.start_time is None:
            return 0

        return int(time.time() - self.start_time)