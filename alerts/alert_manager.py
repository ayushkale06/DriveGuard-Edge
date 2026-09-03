import time


class AlertManager:

    def __init__(self):

        self.last_alert = 0
        self.cooldown = 3

    def get_alert(self, info):

        current = time.time()

        if current - self.last_alert < self.cooldown:
            return None

        # Highest Priority

        if info["driver"] == "DROWSY":

            self.last_alert = current

            return {
                "level": "CRITICAL",
                "message": "Driver is drowsy!"
            }

        if info["phone"] == "DETECTED":

            self.last_alert = current

            return {
                "level": "HIGH",
                "message": "Phone usage detected!"
            }

        if info.get("yawning", False):

            self.last_alert = current

            return {
                "level": "MEDIUM",
                "message": "Driver is yawning."
            }

        if info.get("head") != "FORWARD":

            self.last_alert = current

            return {
                "level": "LOW",
                "message": "Keep eyes on the road."
            }

        return None