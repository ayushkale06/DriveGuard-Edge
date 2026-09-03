class Settings:

    def __init__(self):

        self.face_detection = True
        self.face_mesh = True
        self.eye_tracking = True
        self.blink_detection = True
        self.drowsiness = True
        self.head_pose = True
        self.yawn_detection = True
        self.phone_detection = True
        self.seatbelt_detection = True

        self.voice_alert = True
        self.screenshot = True
        self.event_logger = True
        self.pdf_reports = True

settings = Settings()