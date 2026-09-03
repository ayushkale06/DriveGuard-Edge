import cv2
import numpy as np


class HeadPoseDetector:

    def __init__(self):

        # Face landmarks used for head pose estimation
        self.landmark_ids = [33, 263, 1, 61, 291, 199]

    def detect(self, frame, face_landmarks):

        h, w, _ = frame.shape

        face_2d = []
        face_3d = []

        for idx in self.landmark_ids:

            lm = face_landmarks.landmark[idx]

            x = lm.x * w
            y = lm.y * h
            z = lm.z * w

            face_2d.append([x, y])
            face_3d.append([x, y, z])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        focal_length = w

        cam_matrix = np.array(
            [
                [focal_length, 0, w / 2],
                [0, focal_length, h / 2],
                [0, 0, 1]
            ],
            dtype=np.float64
        )

        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rotation_vec, translation_vec = cv2.solvePnP(
            face_3d,
            face_2d,
            cam_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:

            return {
                "direction": "UNKNOWN",
                "pitch": 0.0,
                "yaw": 0.0,
                "roll": 0.0
            }

        rotation_matrix, _ = cv2.Rodrigues(rotation_vec)

        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)

        # OpenCV already returns degrees
        pitch = float(angles[0])
        yaw = float(angles[1])
        roll = float(angles[2])

        direction = "FORWARD"

        # LEFT / RIGHT

        if yaw < -15:
            direction = "LEFT"

        elif yaw > 15:
            direction = "RIGHT"

        # UP / DOWN

        elif pitch < -12:
            direction = "DOWN"

        elif pitch > 12:
            direction = "UP"

        return {

            "direction": direction,

            "pitch": round(pitch, 1),

            "yaw": round(yaw, 1),

            "roll": round(roll, 1)

        }