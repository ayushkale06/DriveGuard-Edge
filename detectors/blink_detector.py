class BlinkDetector:

    def __init__(self):

        self.EAR_THRESHOLD = 0.21
        self.CONSEC_FRAMES = 3

        self.counter = 0
        self.total_blinks = 0
        self.eye_closed = False

    def detect(self, ear):

        if ear < self.EAR_THRESHOLD:

            self.counter += 1

            self.eye_closed = True

        else:

            if self.counter >= self.CONSEC_FRAMES:

                self.total_blinks += 1

            self.counter = 0

            self.eye_closed = False

        return {
            "blink_count": self.total_blinks,
            "eye_closed": self.eye_closed,
            "counter": self.counter
        }