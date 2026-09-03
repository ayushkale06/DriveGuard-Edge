import time
import os
import glob
import av
import cv2
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from streamlit_webrtc import (
    webrtc_streamer,
    VideoProcessorBase,
    RTCConfiguration
)

from monitoring.frame_processor import process_frame

from utils.dashboard import DashboardData
from utils.analytics import Analytics
from utils.pdf_report import PDFReport
from utils.report_generator import ReportGenerator
from config.settings import settings
from utils.session_manager import SessionManager
from utils.shared_state import shared_state

# ===============================================
# PAGE CONFIGURATION
# ===============================================

st.set_page_config(

    page_title="DriveGuard Edge",

    page_icon="🚗",

    layout="wide",

    initial_sidebar_state="expanded"

)

# ===============================================
# DASHBOARD OBJECT
# ===============================================

dashboard = DashboardData()
report_generator = ReportGenerator()
analytics = Analytics()
report = PDFReport()
session = SessionManager()

# ===============================================
# CSS
# ===============================================

st.markdown("""

<style>

.main{

    background:#0E1117;

}

.block-container{

    padding-top:0.8rem;

}

h1{

    color:#00E5FF;

    text-align:center;

}

div[data-testid="metric-container"]{

    background:#161B22;

    border-radius:15px;

    padding:12px;

    border:1px solid #2A2F3A;

    box-shadow:0px 0px 8px rgba(0,0,0,0.4);

}

hr{

    border-color:#2A2F3A;

}

</style>

""", unsafe_allow_html=True)

# ===============================================
# SIDEBAR
# ===============================================

st.sidebar.title("🚗 DriveGuard Edge")

st.sidebar.subheader("Session")

col1, col2 = st.sidebar.columns(2)

with col1:

    if st.button("▶ Start"):

        session.start()

with col2:

    if st.button("⏹ Stop"):

        session.stop()

col3, col4 = st.sidebar.columns(2)

with col3:

    if st.button("⏸ Pause"):

        session.pause()

with col4:

    if st.button("▶ Resume"):

        session.resume()

st.sidebar.markdown("---")

st.sidebar.markdown("### Camera")

camera = st.sidebar.selectbox(

    "Select Camera",

    [

        "Default Camera"

    ]

)

st.sidebar.markdown("---")

st.sidebar.subheader("AI Modules")

settings.face_detection = st.sidebar.checkbox(
    "Face Detection",
    settings.face_detection
)

settings.face_mesh = st.sidebar.checkbox(
    "Face Mesh",
    settings.face_mesh
)

settings.eye_tracking = st.sidebar.checkbox(
    "Eye Tracking",
    settings.eye_tracking
)

settings.blink_detection = st.sidebar.checkbox(
    "Blink Detection",
    settings.blink_detection
)

settings.drowsiness = st.sidebar.checkbox(
    "Drowsiness Detection",
    settings.drowsiness
)

settings.head_pose = st.sidebar.checkbox(
    "Head Pose",
    settings.head_pose
)

settings.yawn_detection = st.sidebar.checkbox(
    "Yawn Detection",
    settings.yawn_detection
)

settings.phone_detection = st.sidebar.checkbox(
    "Phone Detection",
    settings.phone_detection
)

settings.seatbelt_detection = st.sidebar.checkbox(
    "Seatbelt Detection",
    settings.seatbelt_detection
)

settings.voice_alert = st.sidebar.checkbox(
    "Voice Alerts",
    settings.voice_alert
)

settings.screenshot = st.sidebar.checkbox(
    "Screenshot Capture",
    settings.screenshot
)

settings.event_logger = st.sidebar.checkbox(
    "Event Logger",
    settings.event_logger
)

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Reset Statistics"):

    dashboard.reset()

if st.sidebar.button("💾 Save Session"):

    st.success("Session saved successfully.")

st.sidebar.markdown("---")

st.sidebar.success("System Ready")

st.sidebar.info(

    """
Modules Active

✅ Face Detection

✅ Face Mesh

✅ Eye Tracking

✅ Blink

✅ Drowsiness

✅ Head Pose

✅ Yawn

✅ Phone Detection

✅ Risk Engine

"""
)

# ===============================================
# TITLE
# ===============================================

st.title("🚗 DriveGuard Edge")

st.caption(

    "AI Powered Driver Monitoring & Safety System"

)
# ==========================================================
# VIDEO PROCESSOR
# ==========================================================

class VideoProcessor(VideoProcessorBase):

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        img, info = process_frame(img)

        print("RECV:", info)

        dashboard.update(info)

        analytics.update(info)

        shared_state.update(info)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ==========================================================
# WEBRTC CONFIGURATION
# ==========================================================

RTC_CONFIGURATION = RTCConfiguration({

    "iceServers":[

        {

            "urls":[

                "stun:stun.l.google.com:19302"

            ]

        }

    ]

})

# ==========================================================
# PAGE LAYOUT
# ==========================================================

left, right = st.columns(

    [3,1],

    gap="large"

)

# ==========================================================
# CAMERA PANEL
# ==========================================================

with left:

    st.subheader("📹 Live Driver Camera")

    camera_ctx = webrtc_streamer(

        key="driveguard",

        video_processor_factory=VideoProcessor,

        rtc_configuration=RTC_CONFIGURATION,

        media_stream_constraints={

            "video":True,

            "audio":False

        },

        async_processing=True

    )

    st.markdown("---")

    st.info(

        """
### AI Modules Running

✔ Face Detection

✔ Face Mesh

✔ Eye Tracking

✔ Blink Detection

✔ Drowsiness Detection

✔ Head Pose Estimation

✔ Yawn Detection

✔ Phone Detection (YOLOv8)

✔ Driver State Engine

✔ Risk Engine

✔ Alert Manager
"""
    )
    # ==========================================================
# RIGHT DASHBOARD
# ==========================================================

with right:

    print("UI:", shared_state.get())

    info = shared_state.get()

    # ======================================================
    # DRIVER STATUS
    # ======================================================

    st.subheader("🚘 Driver Status")

    driver = info.get("driver", "UNKNOWN")

    if driver == "SAFE":

        st.success("🟢 DRIVER SAFE")

    elif driver == "DROWSY":

        st.error("🔴 DRIVER DROWSY")

    elif driver == "PHONE DETECTED":

        st.error("📱 PHONE DETECTED")

    elif driver == "DISTRACTED":

        st.warning("🟠 DRIVER DISTRACTED")

    elif driver == "YAWNING":

        st.warning("🥱 DRIVER YAWNING")

    else:

        st.info(driver)

    # ======================================================
    # ALERT
    # ======================================================

    alert = info.get("alert")

    if alert:

        st.error("🚨 " + alert["message"])

    else:

        st.success("✅ No Active Alert")

    # ======================================================
    # RISK
    # ======================================================

    st.metric(

        "Risk Score",

        f'{info.get("risk_score",100)}%'

    )

    st.metric(

        "Risk Level",

        info.get("risk_status","SAFE")

    )

    st.markdown("---")

    # ======================================================
    # FACE
    # ======================================================

    st.subheader("👤 Face")

    st.metric(

        "Faces",

        info.get("faces",0)

    )

    st.metric(

        "Head",

        info.get("head","FORWARD")

    )

    # ======================================================
    # EYES
    # ======================================================

    st.subheader("👀 Eyes")

    st.metric(

        "Status",

        info.get("eyes","--")

    )

    st.metric(

        "EAR",

        info.get("ear",0)

    )

    st.metric(

        "Blinks",

        info.get("blinks",0)

    )

    # ======================================================
    # MOUTH
    # ======================================================

    st.subheader("🥱 Mouth")

    st.metric(

        "Yawns",

        info.get("yawns",0)

    )

    st.metric(

        "MAR",

        info.get("mar",0)

    )

    # ======================================================
    # PHONE
    # ======================================================

    st.subheader("📱 Phone")

    phone = info.get("phone","NO")

    if phone == "YES":

        st.error("PHONE DETECTED")

    else:

        st.success("NO PHONE")

    # ======================================================
    # SEATBELT
    # ======================================================

    st.subheader("🪑 Seatbelt")

    st.metric(

        "Status",

        info.get("seatbelt","--")

    )

    # ======================================================
    # EMOTION
    # ======================================================

    st.subheader("😊 Emotion")

    st.metric(

        "Emotion",

        info.get("emotion","--")

    )

    st.metric(

        "Confidence",

        f"{info.get('emotion_confidence', 0)}%"

    )

    # ======================================================
    # PERFORMANCE
    # ======================================================

    st.subheader("⚡ Performance")

    st.metric(

        "FPS",

        info.get("fps",0)

    )

    st.metric(

        "Voice Engine",

        info.get("voice", "Ready")

    )

    st.markdown("---")

    # ======================================================
    # TRIP STATISTICS
    # ======================================================

    st.subheader("📊 Trip Statistics")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(

            "Blinks",

            dashboard.total_blinks

        )

        st.metric(

            "Yawns",

            dashboard.total_yawns

        )

        st.metric(

            "Phone",

            dashboard.phone_events

        )

    with col2:

        st.metric(

            "Drowsy",

            dashboard.drowsy_events

        )

        st.metric(

            "Distracted",

            dashboard.distraction_events

        )

        st.metric(

            "Trip",

            f"{dashboard.trip_time()} s"

        )

    # ======================================================
    # LIVE ANALYTICS
    # ======================================================

    st.markdown("---")

    st.subheader("📈 Live Analytics")

    if len(analytics.timestamps) == len(analytics.risk_scores) and len(analytics.timestamps) > 1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=analytics.timestamps,
                y=analytics.risk_scores,
                mode="lines",
                name="Risk Score"
            )
        )

        fig.update_layout(
            title="Risk Score Over Time",
            xaxis_title="Time (sec)",
            yaxis_title="Risk Score",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Collecting risk data...")

    if len(analytics.timestamps) == len(analytics.blinks) and len(analytics.timestamps) > 1:

        fig2 = go.Figure()

        fig2.add_trace(
            go.Scatter(
                x=analytics.timestamps,
                y=analytics.blinks,
                mode="lines",
                name="Blinks"
            )
        )

        fig2.update_layout(
            title="Blink Count",
            xaxis_title="Time (sec)",
            yaxis_title="Blinks",
            height=300
        )

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Collecting blink data...")

    # ======================================================
    # EVENT HISTORY
    # ======================================================

    st.markdown("---")

    st.subheader("📝 Recent Events")

    if os.path.exists("logs/events.csv"):

        df = pd.read_csv("logs/events.csv")

        st.dataframe(

            df.tail(10),

            use_container_width=True,

            hide_index=True

        )

    else:

        st.info("No events recorded yet.")

    # ======================================================
    # LATEST CAPTURE
    # ======================================================

    captures = sorted(

        glob.glob("captures/*.jpg"),

        reverse=True

    )

    st.markdown("---")

    st.subheader("📷 Latest Capture")

    if captures:

        st.image(

            captures[0],

            use_container_width=True

        )

    else:

        st.info(

            "No screenshots yet."

        )

    st.metric(

        "Saved Frames",

        len(captures)

    )

    # ======================================================
    # SYSTEM HEALTH
    # ======================================================

    st.markdown("---")

    st.subheader("💻 System")

    st.success("Camera Connected")

    st.success("YOLO Running")

    st.success("MediaPipe Running")

    st.success("Dashboard Online")

    # ======================================================
    # SESSION
    # ======================================================

    st.markdown("---")

    st.subheader("🕒 Session")

    st.metric(

        "Duration",

        f"{session.duration()} sec"

    )

    st.metric(

        "Status",

        "Running" if session.running() else "Stopped"

    )

    # ======================================================
    # REPORTS
    # ======================================================

    st.markdown("---")

    st.subheader("📄 Reports")

    if st.button("Generate Trip Report"):

        pdf = report.generate(
            dashboard,
            shared_state.get()
        )

        st.success("Report Generated Successfully!")

        with open(pdf, "rb") as f:

            st.download_button(
                "⬇ Download Report",
                f,
                file_name=pdf.split("/")[-1],
                mime="application/pdf"
            )

    st.markdown("---")

    st.subheader("📄 Reports")

    if st.button(
        "📄 Generate Trip Report",
        use_container_width=True
    ):

        filename = report_generator.generate(dashboard)

        st.success("Trip report generated successfully!")

        st.info(f"Saved to:\n{filename}")