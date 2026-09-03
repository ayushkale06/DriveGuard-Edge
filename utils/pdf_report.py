import os
import glob
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet


class PDFReport:

    def __init__(self):

        os.makedirs("reports", exist_ok=True)

    def generate(self, dashboard, info):

        filename = datetime.now().strftime(
            "reports/Trip_%Y%m%d_%H%M%S.pdf"
        )

        doc = SimpleDocTemplate(filename)

        styles = getSampleStyleSheet()

        elements = []

        elements.append(
            Paragraph(
                "<b><font size=18>DriveGuard Edge</font></b>",
                styles["Title"]
            )
        )

        elements.append(
            Paragraph(
                "AI Driver Monitoring Report",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1,20))

        elements.append(
            Paragraph(
                f"<b>Driver State:</b> {info['driver']}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Risk Score:</b> {info['risk_score']}%",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Risk Level:</b> {info['risk_status']}",
                styles["BodyText"]
            )
        )

        elements.append(Spacer(1,15))

        elements.append(
            Paragraph(
                "<b>Trip Statistics</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Paragraph(
                f"Total Blinks : {dashboard.total_blinks}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Total Yawns : {dashboard.total_yawns}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Phone Alerts : {dashboard.phone_events}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Drowsy Alerts : {dashboard.drowsy_events}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Distraction Alerts : {dashboard.distraction_events}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Trip Time : {dashboard.trip_time()} sec",
                styles["BodyText"]
            )
        )

        elements.append(Spacer(1,20))

        captures = sorted(
            glob.glob("captures/*.jpg"),
            reverse=True
        )

        if captures:

            elements.append(
                Paragraph(
                    "<b>Latest Capture</b>",
                    styles["Heading2"]
                )
            )

            elements.append(
                Image(
                    captures[0],
                    width=320,
                    height=240
                )
            )

        doc.build(elements)

        return filename