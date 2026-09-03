class DriverState:

    def __init__(self):

        self.state = "SAFE"
        self.color = (0, 255, 0)

    # ==================================================
    # Driver State Decision Engine
    # ==================================================

    def update(
        self,
        drowsiness,
        yawning,
        head_direction,
        phone=False,
        seatbelt=True
    ):

        # -----------------------------------------
        # Priority 1 : Drowsiness
        # -----------------------------------------

        if drowsiness:

            self.state = "DROWSY"
            self.color = (0, 0, 255)

        # -----------------------------------------
        # Priority 2 : Phone Usage
        # -----------------------------------------

        elif phone:

            self.state = "PHONE DETECTED"
            self.color = (0, 0, 255)

        # -----------------------------------------
        # Priority 3 : Seatbelt
        # -----------------------------------------

        elif not seatbelt:

            self.state = "NO SEATBELT"
            self.color = (0, 0, 255)

        # -----------------------------------------
        # Priority 4 : Head Pose
        # -----------------------------------------

        elif head_direction != "FORWARD":

            self.state = "DISTRACTED"
            self.color = (0, 165, 255)

        # -----------------------------------------
        # Priority 5 : Yawning
        # -----------------------------------------

        elif yawning:

            self.state = "YAWNING"
            self.color = (0, 165, 255)

        # -----------------------------------------
        # Driver Safe
        # -----------------------------------------

        else:

            self.state = "SAFE"
            self.color = (0, 255, 0)

        return {
            "state": self.state,
            "color": self.color
        }