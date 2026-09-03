import math

# Left Eye
LEFT_EYE = [33,160,158,133,153,144]

# Right Eye
RIGHT_EYE = [362,385,387,263,373,380]


class EyeTracker:

    def distance(self, p1, p2):

        return math.sqrt(
            (p1[0]-p2[0])**2 +
            (p1[1]-p2[1])**2
        )

    def ear(self, eye):

        A = self.distance(eye[1], eye[5])
        B = self.distance(eye[2], eye[4])
        C = self.distance(eye[0], eye[3])

        return (A+B)/(2*C)

    def extract(self, frame, landmarks, ids):

        h,w,_ = frame.shape

        points=[]

        for i in ids:

            lm = landmarks.landmark[i]

            x = int(lm.x*w)
            y = int(lm.y*h)

            points.append((x,y))

        return points

    def detect(self, frame, face_landmarks):

        left = self.extract(
            frame,
            face_landmarks,
            LEFT_EYE
        )

        right = self.extract(
            frame,
            face_landmarks,
            RIGHT_EYE
        )

        leftEAR = self.ear(left)
        rightEAR = self.ear(right)

        ear = (leftEAR+rightEAR)/2

        return left,right,ear