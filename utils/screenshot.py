import cv2
import os
import time


class ScreenshotManager:

    def __init__(self):

        os.makedirs("captures", exist_ok=True)

        self.last_capture = 0

        self.cooldown = 5

    def save(self, frame, reason):

        now = time.time()

        if now - self.last_capture < self.cooldown:
            return

        self.last_capture = now

        filename = time.strftime(

            "%Y-%m-%d_%H-%M-%S"

        )

        filename += f"_{reason}.jpg"

        path = os.path.join(

            "captures",

            filename

        )

        cv2.imwrite(path, frame)

        return path