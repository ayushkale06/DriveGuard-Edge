from ultralytics import YOLO


class PhoneDetector:

    def __init__(self):

        # Load YOLOv8 Nano model
        self.model = YOLO("yolov8n.pt")

        # COCO class ID for cell phone
        self.phone_class = 67

    def detect(self, frame):

        phone_detected = False
        confidence = 0.0

        results = self.model(
            frame,
            verbose=False
        )

        for result in results:

            boxes = result.boxes

            for box in boxes:

                cls = int(box.cls[0])

                conf = float(box.conf[0])

                if cls == self.phone_class and conf > 0.50:

                    phone_detected = True
                    confidence = conf

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )

                    # Draw bounding box
                    import cv2

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )

                    cv2.putText(
                        frame,
                        f"PHONE {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

        return {

            "phone": phone_detected,

            "confidence": round(confidence, 2)

        }