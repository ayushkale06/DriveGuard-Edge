class DrowsinessDetector:

    def __init__(self):

        self.EAR_THRESHOLD = 0.21

        self.DROWSY_FRAMES = 20

        self.counter = 0

        self.drowsy = False

    def detect(self, ear):

        if ear < self.EAR_THRESHOLD:

            self.counter += 1

        else:

            self.counter = 0

            self.drowsy = False

        if self.counter >= self.DROWSY_FRAMES:

            self.drowsy = True

        return {

            "drowsy": self.drowsy,

            "counter": self.counter,

            "status": "DROWSY" if self.drowsy else "SAFE"

        }