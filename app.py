import html
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "ReliabilityIQ"
APP_TITLE = "AI-Driven Predictive Maintenance"
APP_SUBTITLE = "Industrial equipment reliability and maintenance intelligence"
APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "machine_data.csv"
DASHBOARD_REFRESH_SECONDS = 15


def local_now():
    try:
        return datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    except Exception:
        return datetime.now()


COLUMNS = [
    "Machine_ID",
    "Machine_Name",
    "Machine_Type",
    "Operating_Hours",
    "Failure_Count",
    "Downtime_Hours",
    "Repair_Time_Hours",
    "Last_Maintenance_Date",
    "Criticality",
]


# ============================================================
# LOGIN SYSTEM
# ============================================================

USERS = {
    "Admin_Nizam": "nizam123",
    "Engineer_Nizam": "nizam123",
    "Engineer_Naim": "naim123",
    "Student_Nizam": "nizam123",
    "Engineer_Haziqah": "haziqah123",
}


def app_logo_svg(size=54):
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <linearGradient id="logoGradient" x1="8" y1="6" x2="64" y2="68" gradientUnits="userSpaceOnUse">
          <stop stop-color="#60A5FA"/>
          <stop offset="0.55" stop-color="#2563EB"/>
          <stop offset="1" stop-color="#14B8A6"/>
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="68" height="68" rx="20" fill="url(#logoGradient)"/>
      <circle cx="31" cy="35" r="11" stroke="white" stroke-width="4"/>
      <path d="M31 17V23M31 47V53M13 35H19M43 35H49M18.5 22.5L22.7 26.7M39.3 43.3L43.5 47.5M18.5 47.5L22.7 43.3M39.3 26.7L43.5 22.5" stroke="white" stroke-width="4" stroke-linecap="round"/>
      <path d="M14 56H25L29 48L35 61L41 51H58" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """


def login_page():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: 1160px !important;
            padding-top: 4.5rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([0.55, 1.15, 0.55])
    with center:
        st.markdown(
            f"""
            <div class="login-brand">
                <div class="login-logo">{app_logo_svg(66)}</div>
                <div>
                    <div class="login-eyebrow">INDUSTRIAL INTELLIGENCE PLATFORM</div>
                    <h1>{APP_NAME}</h1>
                    <p>{APP_TITLE}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(
                """
                <div class="login-copy">
                    <h2>Secure sign in</h2>
                    <p>Access live equipment health, reliability indicators, and maintenance priorities.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your authorised username",
                    autocomplete="username",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    autocomplete="current-password",
                )
                login_button = st.form_submit_button(
                    "Sign in to dashboard",
                    use_container_width=True,
                    type="primary",
                )

            if login_button:
                if username in USERS and USERS[username] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.success("Access granted. Loading dashboard…")
                    st.rerun()
                else:
                    st.error("The username or password is incorrect.")

        st.markdown(
            """
            <div class="login-footer-note">
                <span class="security-dot"></span>
                Protected prototype environment · Authorised users only
            </div>
            """,
            unsafe_allow_html=True,
        )


def check_login():
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("username", "")

    if not st.session_state["logged_in"]:
        login_page()
        st.stop()


def logout_button():
    username = html.escape(st.session_state.get("username", "User"))
    role = username.split("_")[0] if "_" in username else "User"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-user-card">
            <div class="user-avatar">{username[:1].upper()}</div>
            <div class="user-meta">
                <div class="user-name">{username}</div>
                <div class="user-role">{html.escape(role)} access</div>
            </div>
            <span class="online-dot" title="Online"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Sign out", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()


# ============================================================
# SAMPLE DATA
# ============================================================

def create_sample_data():
    sample_data = pd.DataFrame([
        ["M001", "Conveyor Motor", "Motor", 1200, 5, 18, 6, "2026-04-10", "High"],
        ["M002", "Hydraulic Pump", "Pump", 950, 8, 30, 10, "2026-03-25", "High"],
        ["M003", "Air Compressor", "Compressor", 1500, 3, 12, 4, "2026-04-18", "Medium"],
        ["M004", "Cooling Fan", "Fan", 1800, 2, 6, 3, "2026-04-22", "Low"],
        ["M005", "Gearbox Unit", "Gearbox", 1100, 6, 22, 8, "2026-04-05", "High"],
        ["M006", "Packaging Machine", "Production Machine", 2000, 4, 16, 5, "2026-04-12", "Medium"],
        ["M007", "Boiler Feed Pump", "Pump", 870, 7, 28, 9, "2026-03-30", "High"],
        ["M008", "Cooling Tower Fan", "Fan", 1600, 2, 8, 3, "2026-04-20", "Medium"],
        ["M009", "Industrial Mixer", "Mixer", 1400, 5, 20, 7, "2026-04-08", "Medium"],
        ["M010", "Water Chiller", "Chiller", 1250, 6, 24, 8, "2026-04-01", "High"],
        ["M011", "CNC Machine", "Machining Equipment", 2200, 3, 10, 4, "2026-04-21", "Medium"],
        ["M012", "Forklift", "Material Handling", 1000, 4, 14, 5, "2026-04-15", "Medium"],
        ["M013", "Dust Collector", "Support Equipment", 1700, 2, 7, 2, "2026-04-24", "Low"],
        ["M014", "Welding Machine", "Production Equipment", 1300, 3, 9, 3, "2026-04-19", "Low"],
        ["M015", "Generator Set", "Power Equipment", 900, 7, 32, 11, "2026-03-28", "High"],
    ], columns=COLUMNS)

    sample_data.to_csv(DATA_FILE, index=False)


# ============================================================
# DATA FUNCTIONS
# ============================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        create_sample_data()

    df = pd.read_csv(DATA_FILE)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    numeric_cols = [
        "Operating_Hours",
        "Failure_Count",
        "Downtime_Hours",
        "Repair_Time_Hours",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Machine_ID"] = df["Machine_ID"].astype(str)
    df["Machine_Name"] = df["Machine_Name"].astype(str)
    df["Machine_Type"] = df["Machine_Type"].astype(str)
    df["Criticality"] = df["Criticality"].astype(str)

    return df[COLUMNS]


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# ============================================================
# RELIABILITY CALCULATION
# ============================================================

def calculate_reliability(df):
    df = df.copy()

    def calculate_mtbf(row):
        if row["Failure_Count"] > 0:
            return row["Operating_Hours"] / row["Failure_Count"]
        return row["Operating_Hours"]

    def calculate_mttr(row):
        if row["Failure_Count"] > 0:
            return row["Repair_Time_Hours"] / row["Failure_Count"]
        return 0

    def calculate_failure_rate(row):
        if row["Operating_Hours"] > 0:
            return row["Failure_Count"] / row["Operating_Hours"]
        return 0

    df["MTBF"] = df.apply(calculate_mtbf, axis=1)
    df["MTTR"] = df.apply(calculate_mttr, axis=1)

    df["Availability"] = df.apply(
        lambda row: (row["MTBF"] / (row["MTBF"] + row["MTTR"]) * 100)
        if (row["MTBF"] + row["MTTR"]) > 0 else 0,
        axis=1
    )

    df["Failure_Rate"] = df.apply(calculate_failure_rate, axis=1)

    df["MTBF"] = df["MTBF"].round(2)
    df["MTTR"] = df["MTTR"].round(2)
    df["Availability"] = df["Availability"].round(2)
    df["Failure_Rate"] = df["Failure_Rate"].round(5)

    df["Risk_Level"] = df.apply(classify_risk, axis=1)
    df["Maintenance_Priority"] = df["Risk_Level"].apply(get_priority)
    df["Recommendation"] = df.apply(generate_recommendation, axis=1)
    df["Next_Maintenance_Date"] = df.apply(calculate_next_maintenance, axis=1)

    return df


def classify_risk(row):
    availability = row["Availability"]
    failure_count = row["Failure_Count"]
    downtime = row["Downtime_Hours"]
    criticality = row["Criticality"]

    if availability < 85 or failure_count >= 7 or downtime >= 25:
        return "High Risk"

    if criticality == "High" and availability < 90:
        return "High Risk"

    if availability < 95 or failure_count >= 4 or downtime >= 12:
        return "Medium Risk"

    return "Low Risk"


def get_priority(risk_level):
    if risk_level == "High Risk":
        return "Urgent Maintenance"
    if risk_level == "Medium Risk":
        return "Schedule Maintenance Soon"
    return "Continue Monitoring"


def generate_recommendation(row):
    if row["Risk_Level"] == "High Risk":
        return (
            f"{row['Machine_Name']} requires urgent preventive maintenance because it has "
            f"high failure frequency, downtime, or low availability."
        )

    if row["Risk_Level"] == "Medium Risk":
        return (
            f"{row['Machine_Name']} should be scheduled for maintenance soon to prevent "
            f"future breakdown and performance reduction."
        )

    return (
        f"{row['Machine_Name']} is currently stable. Continue normal monitoring and routine inspection."
    )


def calculate_next_maintenance(row):
    try:
        last_date = pd.to_datetime(row["Last_Maintenance_Date"]).date()
    except Exception:
        last_date = date.today()

    if row["Risk_Level"] == "High Risk":
        next_date = last_date + timedelta(days=7)
    elif row["Risk_Level"] == "Medium Risk":
        next_date = last_date + timedelta(days=30)
    else:
        next_date = last_date + timedelta(days=90)

    return next_date.strftime("%Y-%m-%d")




# ============================================================
# MODERN UI HELPERS
# ============================================================


def inject_powerbi_style():
    st.markdown(
        """
        <style>
        :root {
            --surface: #ffffff;
            --surface-soft: #f8fafc;
            --canvas: #f1f5f9;
            --ink: #0f172a;
            --muted: #64748b;
            --line: #e2e8f0;
            --blue: #2563eb;
            --navy: #0f1f3d;
            --teal: #0f9f82;
            --amber: #f59e0b;
            --red: #dc2626;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .stApp,
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 86% 5%, rgba(37, 99, 235, 0.08), transparent 22rem),
                var(--canvas);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: rgba(241, 245, 249, 0.82);
            backdrop-filter: blur(12px);
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        /* Keep the sidebar opener obvious when the sidebar has been collapsed. */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            visibility: visible !important;
            opacity: 1 !important;
            display: block !important;
            position: fixed !important;
            top: 0.75rem !important;
            left: 0.75rem !important;
            z-index: 999999 !important;
        }

        button[data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapsedControl"] button,
        button[data-testid="collapsedControl"],
        [data-testid="collapsedControl"] button {
            min-width: 7.2rem !important;
            height: 2.75rem !important;
            padding: 0 0.9rem !important;
            border: 1px solid rgba(255,255,255,0.24) !important;
            border-radius: 12px !important;
            background: linear-gradient(100deg, #0f1f3d, #2563eb) !important;
            color: #ffffff !important;
            box-shadow: 0 10px 24px rgba(15,31,61,0.28) !important;
        }

        button[data-testid="stSidebarCollapsedControl"]::after,
        [data-testid="stSidebarCollapsedControl"] button::after,
        button[data-testid="collapsedControl"]::after,
        [data-testid="collapsedControl"] button::after {
            content: "  MENU";
            color: #ffffff;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.055em;
        }

        button[data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] button svg,
        button[data-testid="collapsedControl"] svg,
        [data-testid="collapsedControl"] button svg {
            fill: #ffffff !important;
            color: #ffffff !important;
        }

        [data-testid="stSidebarCollapseButton"] button,
        button[data-testid="stSidebarCollapseButton"] {
            border-radius: 9px !important;
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
        }

        .top-menu-title {
            color: #0f172a;
            font-size: 0.98rem;
            font-weight: 800;
            line-height: 1.15;
        }

        .top-menu-help {
            color: #64748b;
            font-size: 0.76rem;
            line-height: 1.35;
        }

        .block-container {
            max-width: 1540px;
            padding-top: 1.15rem;
            padding-bottom: 2.5rem;
        }

        .main h1, .main h2, .main h3, .main h4,
        .main label, .main [data-testid="stWidgetLabel"] p {
            color: var(--ink) !important;
        }

        .main [data-testid="stMarkdownContainer"] > p,
        .main .stCaptionContainer,
        .main small {
            color: var(--muted);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1730 0%, #10213f 55%, #0b1730 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.1rem;
        }

        [data-testid="stSidebar"] * {
            color: #eaf1ff;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.07);
            color: #f8fbff;
            border: 1px solid rgba(255,255,255,0.13);
            border-radius: 10px;
            min-height: 2.45rem;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.13);
            border-color: rgba(255,255,255,0.24);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] > div {
            gap: 0.35rem;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            padding: 0.68rem 0.75rem;
            border-radius: 10px;
            transition: background 120ms ease, transform 120ms ease;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(96, 165, 250, 0.11);
            transform: translateX(2px);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(37,99,235,0.36), rgba(37,99,235,0.12));
            box-shadow: inset 3px 0 0 #60a5fa;
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.72rem;
            padding: 0.35rem 0.1rem 1rem;
        }

        .sidebar-brand-title {
            color: #ffffff;
            font-weight: 800;
            font-size: 1.08rem;
            line-height: 1.15;
        }

        .sidebar-brand-subtitle {
            color: #9fb3d4;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-top: 0.18rem;
        }

        .sidebar-user-card {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            background: rgba(255,255,255,0.055);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 12px;
            padding: 0.72rem;
            margin: 0.35rem 0 0.55rem;
        }

        .user-avatar {
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 10px;
            background: linear-gradient(135deg, #3b82f6, #14b8a6);
            display: grid;
            place-items: center;
            color: white;
            font-weight: 800;
        }

        .user-meta { min-width: 0; flex: 1; }
        .user-name { color: #fff; font-weight: 700; font-size: 0.82rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .user-role { color: #9fb3d4; font-size: 0.7rem; margin-top: 0.12rem; }

        .online-dot, .security-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 0 4px rgba(34,197,94,0.12);
            display: inline-block;
        }

        .sidebar-system-card {
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.085);
            border-radius: 12px;
            padding: 0.78rem;
            margin-top: 0.7rem;
        }

        .sidebar-system-title { color: #9fb3d4; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; }
        .sidebar-system-row { display: flex; justify-content: space-between; gap: 0.5rem; margin-top: 0.48rem; font-size: 0.74rem; }
        .sidebar-system-row span:first-child { color: #9fb3d4; }
        .sidebar-system-row span:last-child { color: #f8fbff; font-weight: 650; text-align: right; }

        .login-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 0 0 1rem;
        }

        .login-logo {
            filter: drop-shadow(0 12px 24px rgba(37,99,235,0.24));
            flex: 0 0 auto;
        }

        .login-eyebrow {
            color: #2563eb;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.13em;
        }

        .login-brand h1 {
            margin: 0.12rem 0 0;
            color: var(--ink);
            font-size: 2.15rem;
            letter-spacing: -0.045em;
        }

        .login-brand p {
            margin: 0.2rem 0 0;
            color: var(--muted);
            font-size: 0.92rem;
        }

        .login-copy h2 { margin: 0; font-size: 1.25rem; color: var(--ink); }
        .login-copy p { margin: 0.3rem 0 1rem; color: var(--muted); font-size: 0.86rem; }
        .login-footer-note { text-align: center; color: #64748b; font-size: 0.74rem; margin-top: 0.85rem; }
        .login-footer-note .security-dot { width: 0.42rem; height: 0.42rem; margin-right: 0.42rem; box-shadow: none; }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,0.9);
            border-color: var(--line) !important;
            border-radius: 16px !important;
            box-shadow: 0 12px 35px rgba(15, 23, 42, 0.07);
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        [data-baseweb="select"] > div,
        [data-baseweb="base-input"] > div {
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: #dbe3ef !important;
            border-radius: 10px !important;
        }

        .stTextInput input::placeholder,
        .stNumberInput input::placeholder {
            color: #94a3b8 !important;
        }

        [data-baseweb="popover"] * {
            color: #0f172a !important;
        }

        .main .stButton > button,
        .main .stDownloadButton > button,
        .main [data-testid="stFormSubmitButton"] > button {
            border-radius: 10px;
            min-height: 2.55rem;
            font-weight: 720;
            border: 1px solid #dbe3ef;
            background: #ffffff;
            color: #172033;
        }

        .main [data-testid="stFormSubmitButton"] > button[kind="primary"],
        .main .stButton > button[kind="primary"] {
            background: linear-gradient(100deg, #2563eb, #1d4ed8);
            color: #ffffff;
            border: none;
            box-shadow: 0 8px 18px rgba(37,99,235,0.2);
        }

        .main .stButton > button:hover,
        .main .stDownloadButton > button:hover {
            border-color: #93b4f8;
            color: #1d4ed8;
        }

        .dashboard-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background:
                radial-gradient(circle at 90% 20%, rgba(96,165,250,0.35), transparent 18rem),
                linear-gradient(105deg, #0b1730 0%, #17356a 62%, #2563eb 100%);
            color: #ffffff;
            border-radius: 18px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 14px 35px rgba(15,31,61,0.2);
            overflow: hidden;
        }

        .dashboard-identity { display: flex; align-items: center; gap: 1rem; min-width: 0; }
        .dashboard-logo { flex: 0 0 auto; filter: drop-shadow(0 10px 18px rgba(0,0,0,0.2)); }
        .dashboard-header h1 { color: #ffffff !important; font-size: 1.72rem; line-height: 1.16; margin: 0; letter-spacing: -0.025em; }
        .dashboard-header p { color: #dce8ff !important; margin: 0.36rem 0 0; font-size: 0.89rem; }
        .dashboard-header-meta { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; justify-content: flex-end; }

        .hero-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.47rem 0.68rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.11);
            border: 1px solid rgba(255,255,255,0.16);
            color: #f8fbff;
            font-size: 0.72rem;
            font-weight: 720;
            white-space: nowrap;
        }

        .live-pulse {
            width: 0.52rem;
            height: 0.52rem;
            border-radius: 999px;
            background: #4ade80;
            box-shadow: 0 0 0 0 rgba(74,222,128,0.65);
            animation: pulse-ring 1.8s infinite;
        }

        @keyframes pulse-ring {
            0% { box-shadow: 0 0 0 0 rgba(74,222,128,0.55); }
            70% { box-shadow: 0 0 0 8px rgba(74,222,128,0); }
            100% { box-shadow: 0 0 0 0 rgba(74,222,128,0); }
        }

        .live-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.65rem;
            background: rgba(255,255,255,0.84);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.68rem;
            margin: 0 0 0.85rem;
            box-shadow: 0 5px 18px rgba(15,23,42,0.045);
        }

        .live-item { padding: 0.18rem 0.55rem; min-width: 0; border-right: 1px solid #edf1f7; }
        .live-item:last-child { border-right: none; }
        .live-label { color: #64748b; text-transform: uppercase; letter-spacing: 0.07em; font-size: 0.61rem; font-weight: 800; }
        .live-value { color: #0f172a; font-size: 0.82rem; font-weight: 760; margin-top: 0.2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .live-value.status-good { color: #07815f; }
        .live-value.status-warning { color: #b45309; }
        .live-value.status-danger { color: #c81e1e; }

        .section-heading {
            display: flex;
            justify-content: space-between;
            align-items: end;
            gap: 1rem;
            margin: 0.15rem 0 0.65rem;
        }
        .section-heading h2 { margin: 0; color: var(--ink); font-size: 1.05rem; letter-spacing: -0.015em; }
        .section-heading p { margin: 0.18rem 0 0; color: var(--muted); font-size: 0.76rem; }

        .kpi-card {
            background: rgba(255,255,255,0.94);
            border: 1px solid var(--line);
            border-radius: 15px;
            padding: 0.92rem 0.96rem;
            min-height: 132px;
            box-shadow: 0 6px 18px rgba(15,23,42,0.055);
            position: relative;
            overflow: hidden;
            transition: transform 150ms ease, box-shadow 150ms ease;
        }

        .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(15,23,42,0.085); }
        .kpi-card::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--kpi-color, #2563eb); }
        .kpi-top { display: flex; justify-content: space-between; gap: 0.5rem; align-items: center; }
        .kpi-icon { width: 2rem; height: 2rem; border-radius: 10px; display: grid; place-items: center; background: color-mix(in srgb, var(--kpi-color) 12%, white); font-size: 1rem; }
        .kpi-badge { color: var(--kpi-color); background: color-mix(in srgb, var(--kpi-color) 9%, white); border: 1px solid color-mix(in srgb, var(--kpi-color) 18%, white); border-radius: 999px; padding: 0.22rem 0.42rem; font-size: 0.58rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; }
        .kpi-label { color: #64748b; font-size: 0.68rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.075em; margin-top: 0.72rem; }
        .kpi-value { color: #0f172a; font-size: 1.72rem; line-height: 1.05; font-weight: 820; margin-top: 0.28rem; letter-spacing: -0.035em; }
        .kpi-note { color: #64748b; font-size: 0.69rem; margin-top: 0.32rem; }

        .insight-box {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            background: #ffffff;
            border: 1px solid var(--line);
            border-left: 4px solid var(--insight-color, #2563eb);
            border-radius: 13px;
            padding: 0.85rem 0.95rem;
            margin: 0.78rem 0 0.9rem;
            color: #334155;
            box-shadow: 0 5px 16px rgba(15,23,42,0.04);
        }
        .insight-symbol { width: 2rem; height: 2rem; display: grid; place-items: center; border-radius: 10px; background: color-mix(in srgb, var(--insight-color) 10%, white); flex: 0 0 auto; }
        .insight-box strong { color: #0f172a; }

        .asset-card {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.82rem;
            box-shadow: 0 5px 16px rgba(15,23,42,0.045);
            min-height: 118px;
        }
        .asset-card-top { display: flex; align-items: center; gap: 0.65rem; }
        .asset-symbol { width: 2.25rem; height: 2.25rem; border-radius: 11px; display: grid; place-items: center; background: #f1f5f9; font-size: 1.1rem; }
        .asset-name { color: #0f172a; font-weight: 780; font-size: 0.82rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .asset-id { color: #64748b; font-size: 0.66rem; margin-top: 0.12rem; }
        .risk-pill { margin-left: auto; border-radius: 999px; padding: 0.24rem 0.45rem; font-size: 0.59rem; font-weight: 820; white-space: nowrap; }
        .risk-high { color: #b91c1c; background: #fef2f2; border: 1px solid #fecaca; }
        .risk-medium { color: #b45309; background: #fffbeb; border: 1px solid #fde68a; }
        .risk-low { color: #047857; background: #ecfdf5; border: 1px solid #a7f3d0; }
        .asset-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.35rem; margin-top: 0.72rem; }
        .asset-stat { background: #f8fafc; border-radius: 9px; padding: 0.42rem; }
        .asset-stat-label { color: #94a3b8; font-size: 0.56rem; text-transform: uppercase; font-weight: 800; }
        .asset-stat-value { color: #334155; font-size: 0.72rem; font-weight: 760; margin-top: 0.12rem; }

        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"] {
            background: rgba(255,255,255,0.94);
            border: 1px solid var(--line);
            border-radius: 15px;
            padding: 0.3rem;
            box-shadow: 0 6px 18px rgba(15,23,42,0.045);
        }

        [data-testid="stDataFrame"] { overflow: hidden; }

        .module-header {
            background: linear-gradient(110deg, #ffffff, #f8fbff);
            border: 1px solid var(--line);
            border-radius: 15px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 5px 16px rgba(15,23,42,0.04);
        }
        .module-header h1 { margin: 0; font-size: 1.4rem; color: #0f172a; }
        .module-header p { margin: 0.3rem 0 0; color: #64748b; font-size: 0.8rem; }

        @media (max-width: 900px) {
            .dashboard-header { align-items: flex-start; flex-direction: column; }
            .dashboard-header-meta { justify-content: flex-start; }
            .live-strip { grid-template-columns: repeat(2, minmax(0,1fr)); }
            .live-item:nth-child(2) { border-right: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def equipment_symbol(machine_type):
    machine_type = str(machine_type).lower()
    if "pump" in machine_type:
        return "💧"
    if "motor" in machine_type or "gear" in machine_type:
        return "⚙️"
    if "compress" in machine_type:
        return "🌀"
    if "fan" in machine_type or "cool" in machine_type or "chiller" in machine_type:
        return "❄️"
    if "forklift" in machine_type or "handling" in machine_type:
        return "🏗️"
    if "weld" in machine_type:
        return "⚡"
    if "generator" in machine_type or "power" in machine_type:
        return "🔋"
    if "cnc" in machine_type or "machin" in machine_type:
        return "🦾"
    if "mixer" in machine_type:
        return "🔄"
    return "🏭"


def render_kpi_card(label, value, note, color, icon, badge):
    st.markdown(
        f"""
        <div class="kpi-card" style="--kpi-color:{color};">
            <div class="kpi-top">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-badge">{html.escape(str(badge))}</div>
            </div>
            <div class="kpi-label">{html.escape(str(label))}</div>
            <div class="kpi-value">{html.escape(str(value))}</div>
            <div class="kpi-note">{html.escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-heading">
            <div>
                <h2>{html.escape(title)}</h2>
                <p>{html.escape(subtitle)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_module_header(title):
    descriptions = {
        "Add Machine": "Register a new industrial asset and its baseline maintenance data.",
        "Update Maintenance Record": "Add the latest operating, failure, downtime, and repair information.",
        "Edit / Delete Machine": "Maintain the master equipment register and correct asset records.",
        "Reliability Analytics": "Analyse MTBF, MTTR, availability, failure frequency, and downtime.",
        "AI Recommendation": "Review risk-based maintenance priorities and recommended actions.",
        "Maintenance Schedule": "Plan upcoming maintenance based on equipment risk and reliability.",
        "About Project": "System scope, indicators, modules, formulas, and industrial benefits.",
    }
    st.markdown(
        f"""
        <div class="module-header">
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(descriptions.get(title, APP_SUBTITLE))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_dashboard_filters(dataframe, selected_types=None, selected_criticality=None, selected_risks=None, search=""):
    filtered = dataframe.copy()
    selected_types = selected_types or []
    selected_criticality = selected_criticality or []
    selected_risks = selected_risks or []

    if selected_types:
        filtered = filtered[filtered["Machine_Type"].isin(selected_types)]
    if selected_criticality:
        filtered = filtered[filtered["Criticality"].isin(selected_criticality)]
    if selected_risks:
        filtered = filtered[filtered["Risk_Level"].isin(selected_risks)]
    if search:
        search_mask = (
            filtered["Machine_ID"].str.contains(search, case=False, na=False)
            | filtered["Machine_Name"].str.contains(search, case=False, na=False)
            | filtered["Machine_Type"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[search_mask]

    return filtered


def get_file_update_time():
    try:
        modified = datetime.fromtimestamp(os.path.getmtime(DATA_FILE), tz=local_now().tzinfo)
        return modified.strftime("%d %b %Y · %H:%M:%S")
    except Exception:
        return "Not available"


def render_live_overview():
    def live_content():
        current_data = calculate_reliability(load_data())
        current_filtered = apply_dashboard_filters(
            current_data,
            st.session_state.get("dashboard_machine_types", []),
            st.session_state.get("dashboard_criticality", []),
            st.session_state.get("dashboard_risk", []),
            st.session_state.get("dashboard_search", ""),
        )

        high_count = int((current_filtered["Risk_Level"] == "High Risk").sum()) if not current_filtered.empty else 0
        overdue_count = 0
        if not current_filtered.empty:
            due_dates = pd.to_datetime(current_filtered["Next_Maintenance_Date"], errors="coerce")
            overdue_count = int((due_dates.dt.date < local_now().date()).sum())

        if high_count > 0:
            health_label = "Attention required"
            health_class = "status-danger"
        elif overdue_count > 0:
            health_label = "Maintenance due"
            health_class = "status-warning"
        else:
            health_label = "Stable operation"
            health_class = "status-good"

        st.markdown(
            f"""
            <div class="live-strip">
                <div class="live-item">
                    <div class="live-label">System status</div>
                    <div class="live-value {health_class}"><span class="live-pulse"></span>&nbsp; {health_label}</div>
                </div>
                <div class="live-item">
                    <div class="live-label">Live asset view</div>
                    <div class="live-value">{len(current_filtered)} assets · {high_count} high risk</div>
                </div>
                <div class="live-item">
                    <div class="live-label">Data source updated</div>
                    <div class="live-value">{get_file_update_time()}</div>
                </div>
                <div class="live-item">
                    <div class="live-label">Malaysia time</div>
                    <div class="live-value">{local_now().strftime('%d %b %Y · %H:%M:%S')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if hasattr(st, "fragment"):
        @st.fragment(run_every=f"{DASHBOARD_REFRESH_SECONDS}s")
        def live_fragment():
            live_content()
        live_fragment()
    else:
        live_content()


def render_asset_cards(dataframe, maximum=3):
    priority_order = {"High Risk": 3, "Medium Risk": 2, "Low Risk": 1}
    assets = dataframe.copy()
    assets["Priority_Order"] = assets["Risk_Level"].map(priority_order).fillna(0)
    assets["Next_Maintenance_Date"] = pd.to_datetime(assets["Next_Maintenance_Date"], errors="coerce")
    assets = assets.sort_values(
        ["Priority_Order", "Downtime_Hours", "Failure_Count"],
        ascending=[False, False, False],
    ).head(maximum)

    columns = st.columns(maximum)
    for col, (_, row) in zip(columns, assets.iterrows()):
        risk_class = {
            "High Risk": "risk-high",
            "Medium Risk": "risk-medium",
            "Low Risk": "risk-low",
        }.get(row["Risk_Level"], "risk-low")
        next_date = row["Next_Maintenance_Date"]
        next_text = next_date.strftime("%d %b") if pd.notna(next_date) else "Not set"
        with col:
            st.markdown(
                f"""
                <div class="asset-card">
                    <div class="asset-card-top">
                        <div class="asset-symbol">{equipment_symbol(row['Machine_Type'])}</div>
                        <div style="min-width:0;">
                            <div class="asset-name">{html.escape(str(row['Machine_Name']))}</div>
                            <div class="asset-id">{html.escape(str(row['Machine_ID']))} · {html.escape(str(row['Machine_Type']))}</div>
                        </div>
                        <div class="risk-pill {risk_class}">{html.escape(str(row['Risk_Level']))}</div>
                    </div>
                    <div class="asset-stats">
                        <div class="asset-stat"><div class="asset-stat-label">Availability</div><div class="asset-stat-value">{row['Availability']:.1f}%</div></div>
                        <div class="asset-stat"><div class="asset-stat-label">Downtime</div><div class="asset-stat-value">{row['Downtime_Hours']:.1f} h</div></div>
                        <div class="asset-stat"><div class="asset-stat-label">Next due</div><div class="asset-stat-value">{next_text}</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def apply_powerbi_chart_layout(fig, height=360, show_legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=22, r=22, t=58, b=26),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial", color="#334155", size=11),
        title_font=dict(size=15, color="#0f172a", family="Inter, Arial"),
        title_x=0.02,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
        ),
        showlegend=show_legend,
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter, Arial"),
        hovermode="closest",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#dce3ee", tickfont=dict(color="#64748b"))
    fig.update_yaxes(gridcolor="#edf1f7", zeroline=False, linecolor="#dce3ee", tickfont=dict(color="#64748b"))
    return fig


# ============================================================
# STREAMLIT PAGE SETUP
# ============================================================

st.set_page_config(
    page_title=f"{APP_NAME} | Predictive Maintenance",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_powerbi_style()
check_login()


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()
df_result = calculate_reliability(df)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown(
    f"""
    <div class="sidebar-brand">
        <div>{app_logo_svg(43)}</div>
        <div>
            <div class="sidebar-brand-title">{APP_NAME}</div>
            <div class="sidebar-brand-subtitle">Equipment intelligence</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

logout_button()
st.sidebar.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)

module_labels = {
    "Dashboard": "▦  Executive Dashboard",
    "Add Machine": "＋  Add Machine",
    "Update Maintenance Record": "↻  Update Maintenance",
    "Edit / Delete Machine": "✎  Manage Assets",
    "Reliability Analytics": "⌁  Reliability Analytics",
    "AI Recommendation": "✦  AI Recommendations",
    "Maintenance Schedule": "▣  Maintenance Schedule",
    "About Project": "ⓘ  About Project",
}

module_keys = list(module_labels.keys())

# Keep the left sidebar and the always-visible page menu synchronized.
st.session_state.setdefault("active_module", "Dashboard")
if st.session_state["active_module"] not in module_keys:
    st.session_state["active_module"] = "Dashboard"
st.session_state.setdefault("sidebar_module", st.session_state["active_module"])
st.session_state.setdefault("top_module", st.session_state["active_module"])


def sync_module_navigation(source_key, target_key):
    selected = st.session_state.get(source_key, "Dashboard")
    if selected not in module_keys:
        selected = "Dashboard"
    st.session_state["active_module"] = selected
    st.session_state[target_key] = selected


st.sidebar.radio(
    "Workspace",
    module_keys,
    format_func=lambda item: module_labels[item],
    label_visibility="collapsed",
    key="sidebar_module",
    on_change=sync_module_navigation,
    args=("sidebar_module", "top_module"),
)

st.sidebar.markdown("<div style='height:0.45rem'></div>", unsafe_allow_html=True)
last_sync = get_file_update_time()
st.sidebar.markdown(
    f"""
    <div class="sidebar-system-card">
        <div class="sidebar-system-title">Data connection</div>
        <div class="sidebar-system-row"><span>Status</span><span><span class="online-dot"></span>&nbsp; Connected</span></div>
        <div class="sidebar-system-row"><span>Source</span><span>{html.escape(Path(DATA_FILE).name)}</span></div>
        <div class="sidebar-system-row"><span>Last update</span><span>{html.escape(last_sync)}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Always-visible navigation. Users can change pages here even if the sidebar is hidden.
with st.container(border=True):
    nav_title_col, nav_select_col, nav_help_col = st.columns(
        [0.9, 2.15, 2.7],
        vertical_alignment="center",
    )
    with nav_title_col:
        st.markdown(
            '<div class="top-menu-title">☰ PAGE MENU</div>',
            unsafe_allow_html=True,
        )
    with nav_select_col:
        st.selectbox(
            "Choose a page",
            module_keys,
            format_func=lambda item: module_labels[item],
            key="top_module",
            on_change=sync_module_navigation,
            args=("top_module", "sidebar_module"),
        )
    with nav_help_col:
        st.markdown(
            '<div class="top-menu-help">Use this menu at any time. The blue <b>MENU</b> button in the upper-left corner also opens the full sidebar.</div>',
            unsafe_allow_html=True,
        )

menu = st.session_state.get("active_module", "Dashboard")

if menu != "Dashboard":
    render_module_header(menu)


# ============================================================
# DASHBOARD MODULE
# ============================================================

if menu == "Dashboard":
    st.markdown(
        f"""
        <div class="dashboard-header">
            <div class="dashboard-identity">
                <div class="dashboard-logo">{app_logo_svg(58)}</div>
                <div>
                    <h1>Predictive Maintenance Executive Dashboard</h1>
                    <p>Live reliability, risk, downtime, and maintenance-priority intelligence.</p>
                </div>
            </div>
            <div class="dashboard-header-meta">
                <span class="hero-chip"><span class="live-pulse"></span> LIVE MONITORING</span>
                <span class="hero-chip">⚙ {len(df_result)} CONNECTED ASSETS</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_live_overview()

    # ------------------------
    # Dashboard filters
    # ------------------------
    filter_title_col, filter_action_col = st.columns([6, 1])
    with filter_title_col:
        render_section_heading(
            "Asset filters",
            "Narrow the live view by equipment type, criticality, risk, or asset identity.",
        )
    with filter_action_col:
        if st.button("↺ Reset filters", use_container_width=True):
            st.session_state["dashboard_machine_types"] = []
            st.session_state["dashboard_criticality"] = []
            st.session_state["dashboard_risk"] = []
            st.session_state["dashboard_search"] = ""
            st.rerun()

    machine_type_options = sorted(df_result["Machine_Type"].dropna().unique().tolist())
    criticality_options = [
        item for item in ["High", "Medium", "Low"]
        if item in df_result["Criticality"].unique()
    ]
    risk_options = [
        item for item in ["High Risk", "Medium Risk", "Low Risk"]
        if item in df_result["Risk_Level"].unique()
    ]

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1.2, 1.05, 1.05, 1.55])
    with filter_col1:
        selected_types = st.multiselect(
            "Machine type",
            machine_type_options,
            placeholder="All machine types",
            key="dashboard_machine_types",
        )
    with filter_col2:
        selected_criticality = st.multiselect(
            "Criticality",
            criticality_options,
            placeholder="All levels",
            key="dashboard_criticality",
        )
    with filter_col3:
        selected_risks = st.multiselect(
            "Risk level",
            risk_options,
            placeholder="All risks",
            key="dashboard_risk",
        )
    with filter_col4:
        search = st.text_input(
            "Search asset",
            placeholder="Machine ID, name, or type",
            key="dashboard_search",
        )

    filtered_df = apply_dashboard_filters(
        df_result,
        selected_types,
        selected_criticality,
        selected_risks,
        search,
    )

    if filtered_df.empty:
        st.warning("No machine records match the selected filters. Reset the filters to restore the full view.")
        st.stop()

    # ------------------------
    # KPI cards
    # ------------------------
    total_machines = len(filtered_df)
    urgent_count = int((filtered_df["Risk_Level"] == "High Risk").sum())
    avg_availability = filtered_df["Availability"].mean()
    avg_mtbf = filtered_df["MTBF"].mean()
    total_downtime = filtered_df["Downtime_Hours"].sum()

    render_section_heading(
        "Operational overview",
        "Key reliability indicators for the current filtered asset population.",
    )

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        render_kpi_card("Total assets", f"{total_machines}", "Machines in the current view", "#2563eb", "🏭", "Live view")
    with kpi2:
        availability_badge = "On target" if avg_availability >= 95 else "Below target"
        availability_color = "#0f9f82" if avg_availability >= 95 else "#f59e0b"
        render_kpi_card("Average availability", f"{avg_availability:.2f}%", "Operational target: 95%", availability_color, "⚙️", availability_badge)
    with kpi3:
        render_kpi_card("Average MTBF", f"{avg_mtbf:.1f} h", "Higher values indicate stronger reliability", "#7c3aed", "⏱️", "Reliability")
    with kpi4:
        render_kpi_card("Total downtime", f"{total_downtime:.1f} h", "Accumulated downtime in the current view", "#f59e0b", "⏸️", "Cumulative")
    with kpi5:
        urgent_badge = "Action required" if urgent_count else "Clear"
        urgent_color = "#dc2626" if urgent_count else "#0f9f82"
        render_kpi_card("Urgent assets", f"{urgent_count}", "High-risk machines requiring attention", urgent_color, "⚠️", urgent_badge)

    availability_gap = max(0, 95 - avg_availability)
    priority_order = {"High Risk": 3, "Medium Risk": 2, "Low Risk": 1}
    insight_df = filtered_df.copy()
    insight_df["Priority_Order"] = insight_df["Risk_Level"].map(priority_order)
    worst_machine = insight_df.sort_values(
        ["Priority_Order", "Downtime_Hours", "Failure_Count"],
        ascending=[False, False, False],
    ).iloc[0]

    if urgent_count > 0:
        insight_color = "#dc2626"
        insight_icon = "⚠️"
        insight_text = (
            f"<strong>{urgent_count} asset(s) require urgent maintenance.</strong> "
            f"The highest-priority asset is <strong>{html.escape(str(worst_machine['Machine_ID']))} — "
            f"{html.escape(str(worst_machine['Machine_Name']))}</strong>, with "
            f"{worst_machine['Downtime_Hours']:.1f} downtime hours and "
            f"{worst_machine['Failure_Count']:.0f} recorded failures."
        )
    elif availability_gap > 0:
        insight_color = "#f59e0b"
        insight_icon = "◷"
        insight_text = (
            f"No high-risk asset is detected, but average availability is "
            f"<strong>{availability_gap:.2f} percentage points below</strong> the 95% target."
        )
    else:
        insight_color = "#0f9f82"
        insight_icon = "✓"
        insight_text = (
            "Assets are operating within the defined reliability range. Continue preventive maintenance "
            "and routine condition monitoring."
        )

    st.markdown(
        f"""
        <div class="insight-box" style="--insight-color:{insight_color};">
            <div class="insight-symbol">{insight_icon}</div>
            <div><strong>Management insight</strong><br>{insight_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_section_heading(
        "Priority equipment",
        "The three assets that currently require the closest management attention.",
    )
    render_asset_cards(filtered_df, maximum=min(3, len(filtered_df)))
    st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)

    # ------------------------
    # Primary visuals
    # ------------------------
    risk_colors = {
        "High Risk": "#dc2626",
        "Medium Risk": "#f59e0b",
        "Low Risk": "#0f9f82",
    }

    render_section_heading(
        "Reliability and risk analysis",
        "Interactive charts update immediately when dashboard filters change.",
    )

    visual_left, visual_right = st.columns([0.78, 1.6])
    with visual_left:
        risk_count = (
            filtered_df["Risk_Level"]
            .value_counts()
            .reindex(["High Risk", "Medium Risk", "Low Risk"], fill_value=0)
            .reset_index()
        )
        risk_count.columns = ["Risk_Level", "Count"]

        fig_risk = go.Figure(
            data=[
                go.Pie(
                    labels=risk_count["Risk_Level"],
                    values=risk_count["Count"],
                    hole=0.66,
                    sort=False,
                    marker=dict(
                        colors=[risk_colors.get(level, "#94a3b8") for level in risk_count["Risk_Level"]],
                        line=dict(color="#ffffff", width=4),
                    ),
                    textinfo="label+value",
                    textfont=dict(size=11),
                    hovertemplate="%{label}: %{value} asset(s)<extra></extra>",
                )
            ]
        )
        fig_risk.add_annotation(
            text=f"<b>{total_machines}</b><br><span style='font-size:10px;color:#64748b'>ASSETS</span>",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=22, color="#0f172a"),
        )
        fig_risk.update_layout(title="Risk distribution")
        apply_powerbi_chart_layout(fig_risk, height=390, show_legend=False)
        st.plotly_chart(fig_risk, use_container_width=True, config={"displayModeBar": False})

    with visual_right:
        availability_chart_df = filtered_df.sort_values("Availability", ascending=True)
        focused_min = max(0, min(94, float(availability_chart_df["Availability"].min()) - 1.0))
        fig_availability = px.bar(
            availability_chart_df,
            x="Availability",
            y="Machine_Name",
            orientation="h",
            color="Risk_Level",
            color_discrete_map=risk_colors,
            text="Availability",
            title="Asset availability against the 95% target",
            hover_data={
                "Machine_ID": True,
                "Machine_Type": True,
                "Failure_Count": True,
                "Downtime_Hours": ":.1f",
                "Availability": ":.2f",
            },
        )
        fig_availability.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
        )
        fig_availability.add_vline(
            x=95,
            line_dash="dash",
            line_color="#64748b",
            annotation_text="95% target",
            annotation_position="top",
        )
        fig_availability.update_xaxes(range=[focused_min, 101.8], title="Availability (%) · focused scale")
        fig_availability.update_yaxes(title="", automargin=True)
        apply_powerbi_chart_layout(fig_availability, height=390, show_legend=True)
        st.plotly_chart(fig_availability, use_container_width=True, config={"displayModeBar": False})

    # ------------------------
    # Secondary visuals
    # ------------------------
    visual_bottom_left, visual_bottom_right = st.columns(2)
    with visual_bottom_left:
        performance_df = filtered_df.sort_values("Downtime_Hours", ascending=False)
        fig_performance = px.scatter(
            performance_df,
            x="Failure_Count",
            y="Downtime_Hours",
            size="Operating_Hours",
            color="Risk_Level",
            color_discrete_map=risk_colors,
            hover_name="Machine_Name",
            text="Machine_ID",
            title="Failure frequency versus downtime",
            hover_data={
                "Machine_Type": True,
                "Operating_Hours": ":.0f",
                "Availability": ":.2f",
                "MTBF": ":.2f",
            },
            size_max=38,
        )
        fig_performance.update_traces(textposition="top center", marker=dict(opacity=0.86, line=dict(width=1, color="white")))
        fig_performance.update_xaxes(title="Recorded failures")
        fig_performance.update_yaxes(title="Downtime hours")
        apply_powerbi_chart_layout(fig_performance, height=385, show_legend=True)
        st.plotly_chart(fig_performance, use_container_width=True, config={"displayModeBar": False})

    with visual_bottom_right:
        maintenance_df = filtered_df.copy()
        maintenance_df["Next_Maintenance_Date"] = pd.to_datetime(maintenance_df["Next_Maintenance_Date"], errors="coerce")
        maintenance_df["Days_To_Maintenance"] = (
            maintenance_df["Next_Maintenance_Date"].dt.date - local_now().date()
        ).apply(lambda value: value.days if pd.notna(value) else None)
        maintenance_df["Schedule_Status"] = maintenance_df["Days_To_Maintenance"].apply(
            lambda days: "Overdue" if pd.notna(days) and days < 0 else (
                "Due ≤ 7 days" if pd.notna(days) and days <= 7 else "Scheduled"
            )
        )
        maintenance_df = maintenance_df.sort_values("Days_To_Maintenance").head(10)
        schedule_colors = {"Overdue": "#dc2626", "Due ≤ 7 days": "#f59e0b", "Scheduled": "#2563eb"}

        fig_schedule = px.bar(
            maintenance_df,
            x="Days_To_Maintenance",
            y="Machine_Name",
            orientation="h",
            color="Schedule_Status",
            color_discrete_map=schedule_colors,
            text="Days_To_Maintenance",
            title="Maintenance due status · top 10 assets",
            hover_data={
                "Machine_ID": True,
                "Risk_Level": True,
                "Next_Maintenance_Date": "|%Y-%m-%d",
                "Maintenance_Priority": True,
            },
        )
        fig_schedule.update_traces(
            texttemplate="%{text} d",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
        )
        fig_schedule.add_vline(x=0, line_dash="dash", line_color="#64748b")
        fig_schedule.update_xaxes(title="Days remaining · negative values are overdue")
        fig_schedule.update_yaxes(title="", categoryorder="total descending", automargin=True)
        apply_powerbi_chart_layout(fig_schedule, height=385, show_legend=True)
        st.plotly_chart(fig_schedule, use_container_width=True, config={"displayModeBar": False})

    # ------------------------
    # Priority table
    # ------------------------
    render_section_heading(
        "Asset priority register",
        "Sort, scan, and export the current maintenance-priority view.",
    )

    table_df = filtered_df.copy()
    table_df["Priority_Order"] = table_df["Risk_Level"].map(priority_order)
    table_df = table_df.sort_values(
        by=["Priority_Order", "Downtime_Hours", "Failure_Count"],
        ascending=[False, False, False],
    )
    table_df["Status"] = table_df["Risk_Level"].map(
        {"High Risk": "🔴 High Risk", "Medium Risk": "🟠 Medium Risk", "Low Risk": "🟢 Low Risk"}
    )

    display_table = table_df[
        [
            "Status",
            "Machine_ID",
            "Machine_Name",
            "Machine_Type",
            "Criticality",
            "Availability",
            "MTBF",
            "Failure_Count",
            "Downtime_Hours",
            "Maintenance_Priority",
            "Next_Maintenance_Date",
        ]
    ].copy()
    display_table["Next_Maintenance_Date"] = pd.to_datetime(display_table["Next_Maintenance_Date"], errors="coerce")

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Risk status"),
            "Machine_ID": st.column_config.TextColumn("Asset ID"),
            "Machine_Name": st.column_config.TextColumn("Equipment"),
            "Availability": st.column_config.ProgressColumn("Availability", format="%.2f%%", min_value=0, max_value=100),
            "MTBF": st.column_config.NumberColumn("MTBF (h)", format="%.2f"),
            "Failure_Count": st.column_config.NumberColumn("Failures", format="%d"),
            "Downtime_Hours": st.column_config.NumberColumn("Downtime (h)", format="%.1f"),
            "Next_Maintenance_Date": st.column_config.DateColumn("Next maintenance", format="DD MMM YYYY"),
        },
    )

    download_col, refresh_col, spacer_col = st.columns([1.45, 1, 5])
    csv = table_df.drop(columns=["Priority_Order"], errors="ignore").to_csv(index=False).encode("utf-8")
    with download_col:
        st.download_button(
            label="↓ Export current view",
            data=csv,
            file_name="predictive_maintenance_dashboard.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with refresh_col:
        if st.button("↻ Refresh data", use_container_width=True):
            st.rerun()


# ============================================================
# ADD MACHINE MODULE
# ============================================================

elif menu == "Add Machine":
    st.subheader("➕ Add New Machine")

    with st.form("add_machine_form"):
        machine_id = st.text_input("Machine ID", placeholder="Example: M016")
        machine_name = st.text_input("Machine Name", placeholder="Example: Conveyor Belt")
        machine_type = st.text_input("Machine Type", placeholder="Example: Motor / Pump / Compressor")

        col1, col2 = st.columns(2)

        with col1:
            operating_hours = st.number_input("Operating Hours", min_value=0.0, step=1.0)
            failure_count = st.number_input("Failure Count", min_value=0, step=1)
            downtime_hours = st.number_input("Downtime Hours", min_value=0.0, step=1.0)

        with col2:
            repair_time_hours = st.number_input("Repair Time Hours", min_value=0.0, step=1.0)
            last_maintenance_date = st.date_input("Last Maintenance Date", value=date.today())
            criticality = st.selectbox("Criticality", ["Low", "Medium", "High"])

        submitted = st.form_submit_button("Add Machine")

        if submitted:
            if machine_id.strip() == "" or machine_name.strip() == "":
                st.error("Machine ID and Machine Name cannot be empty.")

            elif machine_id in df["Machine_ID"].values:
                st.error("Machine ID already exists. Please use a different Machine ID.")

            else:
                new_data = pd.DataFrame([{
                    "Machine_ID": machine_id.strip(),
                    "Machine_Name": machine_name.strip(),
                    "Machine_Type": machine_type.strip(),
                    "Operating_Hours": operating_hours,
                    "Failure_Count": failure_count,
                    "Downtime_Hours": downtime_hours,
                    "Repair_Time_Hours": repair_time_hours,
                    "Last_Maintenance_Date": last_maintenance_date.strftime("%Y-%m-%d"),
                    "Criticality": criticality,
                }])

                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"{machine_name} has been added successfully.")
                st.rerun()


# ============================================================
# UPDATE MAINTENANCE RECORD MODULE
# ============================================================

elif menu == "Update Maintenance Record":
    st.subheader("🔧 Update Maintenance Record")

    if df.empty:
        st.warning("No machine data available.")

    else:
        selected_machine = st.selectbox(
            "Select Machine",
            df["Machine_ID"] + " - " + df["Machine_Name"]
        )

        selected_id = selected_machine.split(" - ")[0]
        selected_row = df[df["Machine_ID"] == selected_id].iloc[0]

        st.info(f"Updating record for: {selected_row['Machine_Name']}")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Current Operating Hours", selected_row["Operating_Hours"])
        col2.metric("Current Failure Count", selected_row["Failure_Count"])
        col3.metric("Current Downtime Hours", selected_row["Downtime_Hours"])
        col4.metric("Current Repair Time Hours", selected_row["Repair_Time_Hours"])

        st.divider()

        with st.form("update_record_form"):
            st.write("Enter additional maintenance data:")

            add_operating_hours = st.number_input("Additional Operating Hours", min_value=0.0, step=1.0)
            add_failure_count = st.number_input("Additional Failure Count", min_value=0, step=1)
            add_downtime_hours = st.number_input("Additional Downtime Hours", min_value=0.0, step=1.0)
            add_repair_time_hours = st.number_input("Additional Repair Time Hours", min_value=0.0, step=1.0)
            new_maintenance_date = st.date_input("Latest Maintenance Date", value=date.today())

            update_button = st.form_submit_button("Update Record")

            if update_button:
                index = df[df["Machine_ID"] == selected_id].index[0]

                df.at[index, "Operating_Hours"] += add_operating_hours
                df.at[index, "Failure_Count"] += add_failure_count
                df.at[index, "Downtime_Hours"] += add_downtime_hours
                df.at[index, "Repair_Time_Hours"] += add_repair_time_hours
                df.at[index, "Last_Maintenance_Date"] = new_maintenance_date.strftime("%Y-%m-%d")

                save_data(df)
                st.success("Maintenance record updated successfully.")
                st.rerun()


# ============================================================
# EDIT / DELETE MODULE
# ============================================================

elif menu == "Edit / Delete Machine":
    st.subheader("✏️ Edit or Delete Machine Record")

    if df.empty:
        st.warning("No machine data available.")

    else:
        selected_machine = st.selectbox(
            "Select Machine to Edit or Delete",
            df["Machine_ID"] + " - " + df["Machine_Name"]
        )

        selected_id = selected_machine.split(" - ")[0]
        index = df[df["Machine_ID"] == selected_id].index[0]
        selected_row = df.loc[index]

        with st.form("edit_machine_form"):
            machine_id = st.text_input("Machine ID", value=selected_row["Machine_ID"])
            machine_name = st.text_input("Machine Name", value=selected_row["Machine_Name"])
            machine_type = st.text_input("Machine Type", value=selected_row["Machine_Type"])

            col1, col2 = st.columns(2)

            with col1:
                operating_hours = st.number_input(
                    "Operating Hours",
                    min_value=0.0,
                    value=float(selected_row["Operating_Hours"]),
                    step=1.0
                )
                failure_count = st.number_input(
                    "Failure Count",
                    min_value=0,
                    value=int(selected_row["Failure_Count"]),
                    step=1
                )
                downtime_hours = st.number_input(
                    "Downtime Hours",
                    min_value=0.0,
                    value=float(selected_row["Downtime_Hours"]),
                    step=1.0
                )

            with col2:
                repair_time_hours = st.number_input(
                    "Repair Time Hours",
                    min_value=0.0,
                    value=float(selected_row["Repair_Time_Hours"]),
                    step=1.0
                )

                try:
                    old_date = pd.to_datetime(selected_row["Last_Maintenance_Date"]).date()
                except Exception:
                    old_date = date.today()

                last_maintenance_date = st.date_input("Last Maintenance Date", value=old_date)

                criticality_options = ["Low", "Medium", "High"]

                if selected_row["Criticality"] in criticality_options:
                    criticality_index = criticality_options.index(selected_row["Criticality"])
                else:
                    criticality_index = 0

                criticality = st.selectbox(
                    "Criticality",
                    criticality_options,
                    index=criticality_index
                )

            save_button = st.form_submit_button("Save Changes")

            if save_button:
                if machine_id.strip() == "" or machine_name.strip() == "":
                    st.error("Machine ID and Machine Name cannot be empty.")
                else:
                    df.at[index, "Machine_ID"] = machine_id.strip()
                    df.at[index, "Machine_Name"] = machine_name.strip()
                    df.at[index, "Machine_Type"] = machine_type.strip()
                    df.at[index, "Operating_Hours"] = operating_hours
                    df.at[index, "Failure_Count"] = failure_count
                    df.at[index, "Downtime_Hours"] = downtime_hours
                    df.at[index, "Repair_Time_Hours"] = repair_time_hours
                    df.at[index, "Last_Maintenance_Date"] = last_maintenance_date.strftime("%Y-%m-%d")
                    df.at[index, "Criticality"] = criticality

                    save_data(df)
                    st.success("Machine record updated successfully.")
                    st.rerun()

        st.divider()

        if st.button("Delete Selected Machine"):
            df = df.drop(index).reset_index(drop=True)
            save_data(df)
            st.success("Machine record deleted successfully.")
            st.rerun()


# ============================================================
# RELIABILITY ANALYTICS MODULE
# ============================================================

elif menu == "Reliability Analytics":
    st.subheader("📊 Reliability Analytics")

    if df_result.empty:
        st.warning("No data available for analytics.")

    else:
        avg_mtbf = df_result["MTBF"].mean()
        avg_mttr = df_result["MTTR"].mean()
        avg_availability = df_result["Availability"].mean()
        total_downtime = df_result["Downtime_Hours"].sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Average MTBF", f"{avg_mtbf:.2f} hours")
        col2.metric("Average MTTR", f"{avg_mttr:.2f} hours")
        col3.metric("Average Availability", f"{avg_availability:.2f}%")
        col4.metric("Total Downtime", f"{total_downtime:.2f} hours")

        st.divider()

        st.write("### Availability by Machine")
        fig_availability = px.bar(
            df_result,
            x="Machine_Name",
            y="Availability",
            title="Machine Availability (%)",
            text="Availability"
        )
        st.plotly_chart(fig_availability, use_container_width=True)

        st.write("### Failure Count by Machine")
        fig_failure = px.bar(
            df_result,
            x="Machine_Name",
            y="Failure_Count",
            title="Failure Count by Machine",
            text="Failure_Count"
        )
        st.plotly_chart(fig_failure, use_container_width=True)

        st.write("### Downtime by Machine")
        fig_downtime = px.bar(
            df_result,
            x="Machine_Name",
            y="Downtime_Hours",
            title="Downtime Hours by Machine",
            text="Downtime_Hours"
        )
        st.plotly_chart(fig_downtime, use_container_width=True)

        st.write("### Risk Level Distribution")
        risk_count = df_result["Risk_Level"].value_counts().reset_index()
        risk_count.columns = ["Risk_Level", "Count"]

        fig_risk = px.pie(
            risk_count,
            names="Risk_Level",
            values="Count",
            title="Machine Risk Level Distribution"
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        st.write("### MTBF and MTTR Comparison")
        mtbf_mttr_df = df_result[["Machine_Name", "MTBF", "MTTR"]]

        fig_mtbf_mttr = px.bar(
            mtbf_mttr_df,
            x="Machine_Name",
            y=["MTBF", "MTTR"],
            barmode="group",
            title="MTBF vs MTTR by Machine"
        )
        st.plotly_chart(fig_mtbf_mttr, use_container_width=True)


# ============================================================
# AI RECOMMENDATION MODULE
# ============================================================

elif menu == "AI Recommendation":
    st.subheader("🤖 AI-Based Maintenance Recommendation")

    if df_result.empty:
        st.warning("No data available for recommendation.")

    else:
        priority_order = {
            "High Risk": 3,
            "Medium Risk": 2,
            "Low Risk": 1
        }

        recommendation_df = df_result.copy()
        recommendation_df["Priority_Order"] = recommendation_df["Risk_Level"].map(priority_order)

        recommendation_df = recommendation_df.sort_values(
            by=["Priority_Order", "Downtime_Hours", "Failure_Count"],
            ascending=False
        )

        display_cols = [
            "Machine_ID",
            "Machine_Name",
            "Criticality",
            "MTBF",
            "MTTR",
            "Availability",
            "Failure_Rate",
            "Risk_Level",
            "Maintenance_Priority",
            "Recommendation",
        ]

        st.dataframe(recommendation_df[display_cols], use_container_width=True)

        st.divider()

        st.write("### Machines Requiring Urgent Attention")

        high_risk_df = recommendation_df[recommendation_df["Risk_Level"] == "High Risk"]

        if high_risk_df.empty:
            st.success("No high-risk machine detected. All machines are under acceptable condition.")

        else:
            for _, row in high_risk_df.iterrows():
                st.error(
                    f"🚨 {row['Machine_ID']} - {row['Machine_Name']}: "
                    f"{row['Recommendation']}"
                )

        st.divider()

        st.write("### Maintenance Priority Ranking")

        ranking_cols = [
            "Machine_ID",
            "Machine_Name",
            "Risk_Level",
            "Maintenance_Priority",
            "Failure_Count",
            "Downtime_Hours",
            "Availability",
        ]

        st.dataframe(recommendation_df[ranking_cols], use_container_width=True)


# ============================================================
# MAINTENANCE SCHEDULE MODULE
# ============================================================

elif menu == "Maintenance Schedule":
    st.subheader("📅 Maintenance Schedule Planning")

    if df_result.empty:
        st.warning("No data available for maintenance schedule.")

    else:
        schedule_df = df_result.copy()

        today = date.today()

        schedule_df["Next_Maintenance_Date"] = pd.to_datetime(schedule_df["Next_Maintenance_Date"])
        schedule_df["Days_To_Next_Maintenance"] = schedule_df["Next_Maintenance_Date"].apply(
            lambda x: (x.date() - today).days
        )

        schedule_df = schedule_df.sort_values(by="Next_Maintenance_Date")

        display_schedule = schedule_df[
            [
                "Machine_ID",
                "Machine_Name",
                "Risk_Level",
                "Maintenance_Priority",
                "Last_Maintenance_Date",
                "Next_Maintenance_Date",
                "Days_To_Next_Maintenance",
            ]
        ]

        st.dataframe(display_schedule, use_container_width=True)

        st.divider()

        st.write("### Upcoming Maintenance Chart")

        fig_schedule = px.bar(
            schedule_df,
            x="Machine_Name",
            y="Days_To_Next_Maintenance",
            title="Days to Next Maintenance",
            text="Days_To_Next_Maintenance"
        )
        st.plotly_chart(fig_schedule, use_container_width=True)

        st.info(
            "High-risk machines are scheduled earlier, while low-risk machines have longer monitoring intervals."
        )


# ============================================================
# ABOUT PROJECT MODULE
# ============================================================

elif menu == "About Project":
    st.subheader("ℹ️ About This Project")

    st.write("""
    ### Project Title
    **AI-Driven Predictive Maintenance Scheduling System for Industrial Equipment Reliability Improvement**

    ### Project Concept
    This project is a software-based reliability engineering system. It helps maintenance engineers analyze
    machine condition using reliability indicators and recommend maintenance priority.

    ### Main Objective
    To reduce unexpected machine breakdown, improve maintenance planning, and support industrial decision-making.

    ### Reliability Indicators Used
    - **MTBF**: Mean Time Between Failures
    - **MTTR**: Mean Time To Repair
    - **Availability**
    - **Failure Rate**

    ### System Modules
    1. Login Authentication
    2. Dashboard
    3. Add Machine
    4. Update Maintenance Record
    5. Edit / Delete Machine
    6. Reliability Analytics
    7. AI Recommendation
    8. Maintenance Schedule

    ### Industrial Benefits
    - Reduces machine downtime
    - Improves preventive maintenance planning
    - Helps identify high-risk equipment
    - Supports data-driven decision-making
    - Reduces unnecessary maintenance cost
    - Improves equipment availability and reliability

    ### Hardware Requirement
    This project does not require hardware. It uses simulated or historical machine maintenance data stored in CSV format.

    ### Login Function
    A login authentication function is included to restrict access to authorized users only.
    """)

    st.divider()

    st.write("### Formulas Used")

    st.latex(r"MTBF = \frac{Operating\ Hours}{Failure\ Count}")

    st.latex(r"MTTR = \frac{Repair\ Time\ Hours}{Failure\ Count}")

    st.latex(r"Availability = \frac{MTBF}{MTBF + MTTR} \times 100")

    st.latex(r"Failure\ Rate = \frac{Failure\ Count}{Operating\ Hours}")
