import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


class ReportGenerator:

    def __init__(self):

        os.makedirs("reports", exist_ok=True)

    def generate(self, dashboard):

        filename = datetime.now().strftime(
            "reports/Trip_Report_%Y%m%d_%H%M%S.pdf"
        )

        doc = SimpleDocTemplate(filename)

        styles = getSampleStyleSheet()

        elements = []

        title = Paragraph(
            "<b><font size=22 color='darkblue'>DriveGuard Edge</font></b>",
            styles["Title"]
        )

        elements.append(title)

        elements.append(
            Paragraph(
                "AI Driver Monitoring System",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 20))

        data = [

            ["Metric", "Value"],

            ["Trip Time", dashboard.trip_time()],

            ["Total Blinks", dashboard.total_blinks],

            ["Total Yawns", dashboard.total_yawns],

            ["Phone Events", dashboard.phone_events],

            ["Drowsy Alerts", dashboard.drowsy_events],

            ["Distraction Alerts", dashboard.distraction_events]

        ]

        table = Table(data)

        table.setStyle(

            TableStyle([

                ("BACKGROUND", (0,0), (-1,0), colors.darkblue),

                ("TEXTCOLOR", (0,0), (-1,0), colors.white),

                ("GRID", (0,0), (-1,-1), 1, colors.grey),

                ("BACKGROUND", (0,1), (-1,-1), colors.beige),

                ("ALIGN",(0,0),(-1,-1),"CENTER"),

                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

                ("BOTTOMPADDING",(0,0),(-1,0),10)

            ])

        )

        elements.append(table)

        elements.append(Spacer(1,20))

        elements.append(

            Paragraph(

                "Generated automatically by DriveGuard Edge.",

                styles["Normal"]

            )

        )

        doc.build(elements)

        return filename