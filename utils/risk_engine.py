class RiskEngine:

    def __init__(self):

        self.score = 100

    def calculate(

        self,

        drowsy,

        yawning,

        phone,

        distracted,

        seatbelt

    ):

        score = 100

        # -------------------------

        if drowsy:
            score -= 40

        if yawning:
            score -= 15

        if phone:
            score -= 35

        if distracted:
            score -= 20

        if not seatbelt:
            score -= 25

        score = max(score, 0)

        if score >= 90:

            status = "SAFE"

        elif score >= 70:

            status = "LOW RISK"

        elif score >= 50:

            status = "MEDIUM RISK"

        elif score >= 30:

            status = "HIGH RISK"

        else:

            status = "CRITICAL"

        return {

            "score": score,

            "status": status

        }