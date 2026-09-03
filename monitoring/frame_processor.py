import cv2
import mediapipe as mp

from detectors.head_pose import HeadPoseDetector
from detectors.face_detector import FaceDetector
from detectors.face_mesh import FaceMeshDetector
from detectors.eye_tracker import EyeTracker
from detectors.blink_detector import BlinkDetector
from detectors.drowsiness_detector import DrowsinessDetector
from detectors.yawn_detector import YawnDetector
from detectors.driver_state import DriverState
from detectors.phone_detector import PhoneDetector
from detectors.seatbelt_detector import SeatbeltDetector
from monitoring.risk_engine import RiskEngine
# from detectors.emotion_detector import EmotionDetector
from alerts.alert_manager import AlertManager
from utils.screenshot import ScreenshotManager
from utils.voice_alert import VoiceAlert
from config.settings import settings

# =====================================================
# Initialize AI Modules
# =====================================================

face_detector = FaceDetector()
face_mesh = FaceMeshDetector()
eye_tracker = EyeTracker()
blink_detector = BlinkDetector()
drowsiness_detector = DrowsinessDetector()
head_pose_detector = HeadPoseDetector()
yawn_detector = YawnDetector()
driver_state = DriverState()
phone_detector = PhoneDetector()
seatbelt_detector = SeatbeltDetector()
risk_engine = RiskEngine()
# emotion_detector = EmotionDetector()
alert_manager = AlertManager()
screenshot = ScreenshotManager()
voice = VoiceAlert()

# =============================================
# Frame Scheduler
# =============================================

FRAME_COUNT = 0
LAST_PHONE = {"phone": False, "confidence": 0}
LAST_SEATBELT = {"seatbelt": True, "confidence": 0}
LAST_DRIVER = "SAFE"
LAST_CAPTURE = ""

# =====================================================
# MediaPipe Drawing Utilities
# =====================================================

mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# =====================================================
# Colors
# =====================================================

GREEN = (0,255,0)
RED = (0,0,255)
BLUE = (255,0,0)
YELLOW = (0,255,255)
CYAN = (255,255,0)
WHITE = (255,255,255)
ORANGE = (0,165,255)
MAGENTA = (255,0,255)

# =====================================================
# Process Frame
# =====================================================

def process_frame(frame):

    global FRAME_COUNT
    global LAST_PHONE
    global LAST_SEATBELT
    global LAST_DRIVER
    global LAST_CAPTURE

    FRAME_COUNT += 1

    info = {
    "driver": "NO FACE",
    "faces": 0,
    "ear": 0.0,
    "blinks": 0,
    "eyes": "--",
    "head_pose": "--",
    "pitch": 0.0,
    "yaw": 0.0,
    "emotion": "Neutral",
    "emotion_confidence": 0,
    "seatbelt": "--",
    "phone": "--",
    "fps": "--",
    "mar": 0.0,
    "yawning": False,
    "yawns": 0,
    "risk_score": 100,
    "risk_status": "SAFE",
    "alert": None,
    "voice": "Ready"
}

    # =================================================
    # FACE DETECTION
    # =================================================

    if settings.face_detection:

        faces = face_detector.detect(frame)

    else:

        faces = []

    info["faces"] = len(faces)

    if len(faces) > 0:
        info["driver"] = "SAFE"

    for face in faces:

        x, y, w, h = face["bbox"]
        confidence = face["confidence"]

        cv2.rectangle(
            frame,
            (x,y),
            (x+w,y+h),
            GREEN,
            2
        )

        cv2.putText(
            frame,
            f"{confidence:.2f}",
            (x,y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            GREEN,
            2
        )

    # =================================================
    # FACE MESH
    # =================================================

    mesh_results = face_mesh.detect(frame)

    if mesh_results.multi_face_landmarks:

        for face_landmarks in mesh_results.multi_face_landmarks:

            if settings.face_mesh:

                mp_draw.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style()
                )

            # =============================================
            # Eye Tracking
            # =============================================

            left_eye, right_eye, ear = eye_tracker.detect(
                frame,
                face_landmarks
            )

            info["ear"] = round(ear,2)

            for point in left_eye:
                cv2.circle(frame, point, 2, RED, -1)

            for point in right_eye:
                cv2.circle(frame, point, 2, BLUE, -1)

            # =============================================
            # Blink Detection
            # =============================================

            blink = blink_detector.detect(ear)

            info["blinks"] = blink["blink_count"]

            if blink["eye_closed"]:
                info["eyes"] = "CLOSED"
                eye_color = RED
            else:
                info["eyes"] = "OPEN"
                eye_color = GREEN

            # =============================================
            # Head Pose Detection
            # =============================================

            pose = head_pose_detector.detect(
                frame,
                face_landmarks
            )

            info["head_pose"] = pose["direction"]
            info["pitch"] = pose["pitch"]
            info["yaw"] = pose["yaw"]

            # =============================================
            # Yawn Detection
            # =============================================

            yawn = yawn_detector.detect(
                frame,
                face_landmarks
            )

            info["mar"] = yawn["mar"]
            info["yawning"] = yawn["yawning"]
            info["yawns"] = yawn["yawn_count"]

            for p in yawn["points"]:

                cv2.circle(
                    frame,
                    p,
                    3,
                    (0,255,255),
                    -1
                )

            # =============================================
            # Phone Detection
            # =============================================

            if settings.phone_detection:

                if FRAME_COUNT % 5 == 0:

                    LAST_PHONE = phone_detector.detect(frame)

                phone = LAST_PHONE

            else:

                phone = {

                    "phone": False,

                    "confidence": 0

                }

            info["phone"] = "YES" if phone["phone"] else "NO"

            # =============================================
            # Emotion Detection
            # =============================================

            info["emotion"] = "N/A"
            info["emotion_confidence"] = 0

            # =============================================
            # Seatbelt Detection
            # =============================================

            if settings.seatbelt_detection:

                if FRAME_COUNT % 10 == 0:

                    LAST_SEATBELT = seatbelt_detector.detect(frame)

                seatbelt = LAST_SEATBELT

            else:

                seatbelt = {

                    "seatbelt": True,

                    "confidence": 0

                }

            if seatbelt["seatbelt"]:

                info["seatbelt"] = "YES"

            else:

                info["seatbelt"] = "NO"

            # =============================================
            # Drowsiness Detection
            # =============================================

            drowsiness = drowsiness_detector.detect(ear)

            # =============================================
            # Driver State Decision Engine
            # =============================================

            driver = driver_state.update(

                drowsiness=drowsiness["drowsy"],

                yawning=info["yawning"],

                head_direction=pose["direction"],

                phone=phone["phone"],

                seatbelt=(info["seatbelt"] == "YES")

            )

            info["driver"] = driver["state"]

            driver_color = driver["color"]

            # =============================================
            # Risk Engine
            # =============================================

            score, status = risk_engine.calculate(info)

            info["risk_score"] = score
            info["risk_status"] = status

            # =============================================
            # Emotion-Based Risk Adjustment
            # =============================================

            if info["emotion"] in ["Angry", "Fear", "Sad"]:

                info["risk_score"] -= 10

                info["risk_status"] = "WARNING"

            # =============================================
            # Screenshot Manager
            # =============================================

            capture_event = None

            if info["driver"] == "DROWSY":
                capture_event = "DROWSY"

            elif info["phone"] == "YES":
                capture_event = "PHONE"

            elif info["risk_status"] == "CRITICAL":
                capture_event = "CRITICAL"

            if capture_event:

                if capture_event != LAST_CAPTURE:

                    LAST_CAPTURE = capture_event

                    screenshot.save(frame, capture_event)

            else:

                LAST_CAPTURE = ""

            # ---------------------------------------
            # Voice Alerts
            # ---------------------------------------

            voice_event = None
            voice_message = ""

            if info["driver"] == "DROWSY":
                voice_event = "DROWSY"
                voice_message = "Wake up. Driver appears drowsy."

            elif info["phone"] == "YES":
                voice_event = "PHONE"
                voice_message = "Warning. Phone detected."

            elif info["driver"] == "DISTRACTED":
                voice_event = "DISTRACTED"
                voice_message = "Please keep your eyes on the road."

            elif info["driver"] == "YAWNING":
                voice_event = "YAWNING"
                voice_message = "Driver appears tired. Consider taking a break."

            elif info["risk_status"] == "CRITICAL":
                voice_event = "CRITICAL"
                voice_message = "Critical risk detected."

            if voice_event:

                if voice_event != LAST_DRIVER:

                    LAST_DRIVER = voice_event

                    voice.speak(voice_message)

                info["voice"] = "Speaking"

            else:

                LAST_DRIVER = "SAFE"

                info["voice"] = "Ready"

            # =============================================
            # HUD
            # =============================================

            cv2.putText(
                frame,
                f"Faces : {info['faces']}",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                YELLOW,
                2
            )

            cv2.putText(
                frame,
                f"EAR : {info['ear']:.2f}",
                (20,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                CYAN,
                2
            )

            cv2.putText(
                frame,
                f"Blinks : {info['blinks']}",
                (20,120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                WHITE,
                2
            )

            cv2.putText(
                frame,
                f"Eyes : {info['eyes']}",
                (20,160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                eye_color,
                2
            )

            cv2.putText(
                frame,
                f"Driver : {info['driver']}",
                (20,200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                driver_color,
                2
            )

            cv2.putText(
                frame,
                f"Closed Frames : {drowsiness['counter']}",
                (20,240),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                ORANGE,
                2
            )

            # =============================================
            # Draw Head Pose
            # =============================================

            cv2.putText(
                frame,
                f"Head : {info['head_pose']}",
                (20,280),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                MAGENTA,
                2
            )

            cv2.putText(
                frame,
                f"Pitch : {info['pitch']:.1f}",
                (20,320),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                WHITE,
                2
            )

            cv2.putText(
                frame,
                f"Yaw : {info['yaw']:.1f}",
                (20,360),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                WHITE,
                2
            )

            # =============================================
            # Yawn HUD
            # =============================================

            cv2.putText(
                frame,
                f"MAR : {info['mar']}",
                (20,400),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,0),
                2
            )

            cv2.putText(
                frame,
                f"Yawns : {info['yawns']}",
                (20,440),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,255),
                2
            )

            yawn_status = "NO"

            color = GREEN

            if info["yawning"]:
                yawn_status = "YES"
                color = RED

            cv2.putText(
                frame,
                f"Yawning : {yawn_status}",
                (20,480),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

            # =============================================
            # Phone HUD
            # =============================================

            phone_color = GREEN

            if phone["phone"]:
                phone_color = RED

            cv2.putText(

                frame,

                f"Phone : {info['phone']}",

                (20, 560),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                phone_color,

                2

            )

            # =============================================
            # Risk HUD
            # =============================================

            cv2.putText(

                frame,

                f"Risk : {score}%",

                (20, 520),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (0,255,255),

                2

            )

            cv2.putText(

                frame,

                status,

                (20,560),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0,0,255),

                3

            )

            # =============================================
            # Emotion HUD
            # =============================================

            cv2.putText(

                frame,

                f"Emotion : {info['emotion']}",

                (20, 600),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (255,255,0),

                2

            )

    else:

        info["driver"] = "NO FACE"

        cv2.putText(
            frame,
            "NO FACE DETECTED",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            RED,
            2
        )

    # =====================================================
    # Alert Manager
    # =====================================================

    alert = alert_manager.get_alert(info)

    info["alert"] = alert

    # =====================================================
    # Display Alert on Video
    # =====================================================

    if info["alert"]:

        cv2.rectangle(
            frame,
            (0,0),
            (frame.shape[1],60),
            (0,0,255),
            -1
        )

        cv2.putText(

            frame,

            info["alert"]["message"],

            (20,40),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (255,255,255),

            3

        )

    return frame, info