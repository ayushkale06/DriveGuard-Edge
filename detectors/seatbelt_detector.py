from ultralytics import YOLO
import cv2
import os


class SeatbeltDetector:

    def __init__(self):

        model_path = os.path.join("models", "seatbelt.pt")

        self.available = os.path.exists(model_path)

        if self.available:
            self.model = YOLO(model_path)

    # -------------------------------------------------

    def detect(self, frame):

        # Model not available
        if not self.available:

            return {
                "seatbelt": False,
                "confidence": 0.0
            }

        seatbelt = False
        confidence = 0.0

        results = self.model(
            frame,
            verbose=False
        )

        for result in results:

            for box in result.boxes:

                cls = int(box.cls[0])

                conf = float(box.conf[0])

                # Assumption:
                # class 0 = Seatbelt
                if cls == 0 and conf > 0.50:

                    seatbelt = True
                    confidence = conf

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0,255,0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"SEATBELT {conf:.2f}",
                        (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0,255,0),
                        2
                    )

        return {

            "seatbelt": seatbelt,

            "confidence": round(confidence,2)

        }