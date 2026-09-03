import math

# MediaPipe mouth landmarks
MOUTH = [61, 13, 291, 14]


class YawnDetector:

    def __init__(self):

        self.threshold = 0.60
        self.frames_required = 12

        self.counter = 0
        self.yawn_count = 0

    def distance(self, p1, p2):

        return math.sqrt(
            (p1[0]-p2[0])**2 +
            (p1[1]-p2[1])**2
        )

    def detect(self, frame, face_landmarks):

        h, w, _ = frame.shape

        pts = []

        for idx in MOUTH:

            lm = face_landmarks.landmark[idx]

            pts.append((
                int(lm.x*w),
                int(lm.y*h)
            ))

        left = pts[0]
        top = pts[1]
        right = pts[2]
        bottom = pts[3]

        horizontal = self.distance(left, right)
        vertical = self.distance(top, bottom)

        mar = vertical / horizontal

        if mar > self.threshold:

            self.counter += 1

        else:

            if self.counter >= self.frames_required:
                self.yawn_count += 1

            self.counter = 0

        yawning = self.counter >= self.frames_required

        return {

            "mar": round(mar,2),

            "yawning": yawning,

            "yawn_count": self.yawn_count,

            "points": pts

        }