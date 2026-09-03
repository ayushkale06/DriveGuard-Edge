import cv2
import mediapipe as mp

mp_face = mp.solutions.face_detection


class FaceDetector:

    def __init__(self, confidence=0.5):
        self.detector = mp_face.FaceDetection(
            model_selection=0,
            min_detection_confidence=confidence
        )

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.detector.process(rgb)

        faces = []

        if results.detections:

            h, w, _ = frame.shape

            for detection in results.detections:

                bbox = detection.location_data.relative_bounding_box

                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                bw = int(bbox.width * w)
                bh = int(bbox.height * h)

                confidence = detection.score[0]

                faces.append({
                    "bbox": (x, y, bw, bh),
                    "confidence": confidence
                })

        return faces