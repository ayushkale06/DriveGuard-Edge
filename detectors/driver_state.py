class DriverState:

    def __init__(self):
        pass

    def update(self, drowsiness, yawning, head_direction,
               phone=False, seatbelt=True):

        state = "SAFE"
        color = (0, 255, 0)

        # ------------------------------------
        # Priority 1 : Drowsiness
        # ------------------------------------

        if drowsiness:

            state = "DROWSY"
            color = (0, 0, 255)

        # ------------------------------------
        # Priority 2 : Yawning
        # ------------------------------------

        elif yawning:

            state = "YAWNING"
            color = (0, 165, 255)

        # ------------------------------------
        # Priority 3 : Phone Usage
        # ------------------------------------

        elif phone:

            state = "PHONE DETECTED"
            color = (0, 0, 255)

        # ------------------------------------
        # Priority 4 : Seatbelt
        # ------------------------------------

        elif not seatbelt:

            state = "NO SEATBELT"
            color = (0, 0, 255)

        # ------------------------------------
        # Priority 5 : Looking Away
        # ------------------------------------

        elif head_direction != "FORWARD":

            state = "DISTRACTED"
            color = (0, 165, 255)

        # ------------------------------------
        # Safe
        # ------------------------------------

        return {

            "state": state,

            "color": color

        }