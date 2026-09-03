import pyttsx3
import threading
import time


class VoiceAlert:

    def __init__(self):

        self.engine = pyttsx3.init()

        self.engine.setProperty("rate", 165)

        self.engine.setProperty("volume", 1.0)

        self.last_message = ""

        self.last_time = 0

        self.cooldown = 5

    # ---------------------------------------

    def _speak(self, message):

        self.engine.say(message)

        self.engine.runAndWait()

    # ---------------------------------------

    def speak(self, message):

        now = time.time()

        if message == self.last_message:

            if now - self.last_time < self.cooldown:

                return

        self.last_message = message

        self.last_time = now

        threading.Thread(

            target=self._speak,

            args=(message,),

            daemon=True

        ).start()