class RiskEngine:

    def calculate(self, info):

        score = 100

        # -----------------------------------
        # Phone
        # -----------------------------------

        if info["phone"] == "DETECTED":
            score -= 40

        # -----------------------------------
        # Drowsiness
        # -----------------------------------

        if info["driver"] == "DROWSY":
            score -= 35

        # -----------------------------------
        # Yawning
        # -----------------------------------

        if info.get("yawning", False):
            score -= 15

        # -----------------------------------
        # Looking Away
        # -----------------------------------

        if info.get("head") != "FORWARD":
            score -= 20

        # -----------------------------------
        # No Face
        # -----------------------------------

        if info["faces"] == 0:
            score -= 50

        score = max(score, 0)

        # -----------------------------------
        # Status
        # -----------------------------------

        if score >= 85:
            status = "SAFE"

        elif score >= 65:
            status = "LOW RISK"

        elif score >= 40:
            status = "WARNING"

        elif score >= 20:
            status = "HIGH RISK"

        else:
            status = "CRITICAL"

        return score, status