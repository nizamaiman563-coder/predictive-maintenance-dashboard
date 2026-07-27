import os
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "machine_data.csv"

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
}


def login_page():
    st.title("🔐 AI-Driven Predictive Maintenance Scheduling System for Industrial Equipment")
    st.write("Please enter your username and password to access the system.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_button = st.button("Login")

    if login_button:
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")


def check_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = ""

    if not st.session_state["logged_in"]:
        login_page()
        st.stop()


def logout_button():
    st.sidebar.write(f"Logged in as: **{st.session_state['username']}**")

    if st.sidebar.button("Logout"):
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
# POWER BI-STYLE UI HELPERS
# ============================================================

def inject_powerbi_style():
    st.markdown(
        """
        <style>
        :root {
            --dashboard-bg: #f3f6fb;
            --dashboard-card: #ffffff;
            --dashboard-text: #172033;
            --dashboard-muted: #697386;
            --dashboard-blue: #2463eb;
            --dashboard-navy: #13213c;
            --dashboard-border: #e4e9f2;
        }

        .stApp {
            background: var(--dashboard-bg);
        }

        [data-testid="stHeader"] {
            background: rgba(243, 246, 251, 0.92);
        }

        [data-testid="stSidebar"] {
            background: #101b31;
        }

        [data-testid="stSidebar"] * {
            color: #f7f9fc;
        }

        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
            background: #ffffff;
            color: #172033;
            border-radius: 8px;
        }

        [data-testid="stSidebar"] .stSelectbox svg,
        [data-testid="stSidebar"] .stSelectbox input {
            color: #172033;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.1rem;
            padding-bottom: 2rem;
        }

        .dashboard-header {
            background: linear-gradient(100deg, #13213c 0%, #1c3768 58%, #2463eb 100%);
            color: #ffffff;
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 16px;
            box-shadow: 0 8px 22px rgba(19, 33, 60, 0.16);
        }

        .dashboard-header h1 {
            color: #ffffff;
            font-size: 1.75rem;
            margin: 0 0 6px 0;
            font-weight: 700;
        }

        .dashboard-header p {
            color: #dbe7ff;
            margin: 0;
            font-size: 0.96rem;
        }

        .section-title {
            color: var(--dashboard-text);
            font-size: 1.03rem;
            font-weight: 700;
            margin: 4px 0 8px 0;
        }

        .kpi-card {
            background: var(--dashboard-card);
            border: 1px solid var(--dashboard-border);
            border-radius: 12px;
            padding: 15px 17px;
            min-height: 116px;
            box-shadow: 0 3px 12px rgba(24, 39, 75, 0.06);
            position: relative;
            overflow: hidden;
        }

        .kpi-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 5px;
            background: var(--kpi-color, #2463eb);
        }

        .kpi-label {
            color: var(--dashboard-muted);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.055em;
            margin-left: 3px;
        }

        .kpi-value {
            color: var(--dashboard-text);
            font-size: 1.9rem;
            line-height: 1.1;
            font-weight: 750;
            margin: 9px 0 5px 3px;
        }

        .kpi-note {
            color: var(--dashboard-muted);
            font-size: 0.78rem;
            margin-left: 3px;
        }

        .insight-box {
            background: #ffffff;
            border: 1px solid var(--dashboard-border);
            border-left: 5px solid #2463eb;
            border-radius: 10px;
            padding: 13px 16px;
            margin: 4px 0 12px 0;
            color: var(--dashboard-text);
        }

        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"] {
            background: #ffffff;
            border: 1px solid var(--dashboard-border);
            border-radius: 12px;
            padding: 5px;
            box-shadow: 0 3px 12px rgba(24, 39, 75, 0.05);
        }

        .stDownloadButton > button {
            background: #2463eb;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-weight: 650;
        }

        .stDownloadButton > button:hover {
            background: #1d4ed8;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label, value, note, color):
    st.markdown(
        f"""
        <div class="kpi-card" style="--kpi-color: {color};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_powerbi_chart_layout(fig, height=360, show_legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color="#263248", size=12),
        title_font=dict(size=15, color="#172033"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        showlegend=show_legend,
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#dce3ee")
    fig.update_yaxes(gridcolor="#edf1f7", zeroline=False, linecolor="#dce3ee")
    return fig


# ============================================================
# STREAMLIT PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    page_icon="🛠️",
    layout="wide"
)

inject_powerbi_style()

check_login()
logout_button()


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()
df_result = calculate_reliability(df)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")

menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Dashboard",
        "Add Machine",
        "Update Maintenance Record",
        "Edit / Delete Machine",
        "Reliability Analytics",
        "AI Recommendation",
        "Maintenance Schedule",
        "About Project",
    ]
)

st.sidebar.divider()
st.sidebar.write("Data file:")
st.sidebar.code(DATA_FILE)

if menu != "Dashboard":
    st.title("🛠️ AI-Driven Predictive Maintenance Scheduling System")
    st.caption("Reliability Engineering Dashboard for Industrial Equipment Maintenance")


# ============================================================
# DASHBOARD MODULE
# ============================================================

if menu == "Dashboard":
    st.markdown(
        """
        <div class="dashboard-header">
            <h1>Predictive Maintenance Executive Dashboard</h1>
            <p>Real-time reliability, machine-risk, downtime, and maintenance-priority overview.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------
    # Dashboard slicers
    # ------------------------
    st.markdown('<div class="section-title">Dashboard Filters</div>', unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1.25, 1.25, 1.25, 1.6])

    machine_type_options = sorted(df_result["Machine_Type"].dropna().unique().tolist())
    criticality_options = [
        item for item in ["High", "Medium", "Low"]
        if item in df_result["Criticality"].unique()
    ]
    risk_options = [
        item for item in ["High Risk", "Medium Risk", "Low Risk"]
        if item in df_result["Risk_Level"].unique()
    ]

    with filter_col1:
        selected_types = st.multiselect(
            "Machine Type",
            machine_type_options,
            placeholder="All machine types",
        )

    with filter_col2:
        selected_criticality = st.multiselect(
            "Criticality",
            criticality_options,
            placeholder="All criticality levels",
        )

    with filter_col3:
        selected_risks = st.multiselect(
            "Risk Level",
            risk_options,
            placeholder="All risk levels",
        )

    with filter_col4:
        search = st.text_input(
            "Search Asset",
            placeholder="Machine ID, name, or type",
        )

    filtered_df = df_result.copy()

    if selected_types:
        filtered_df = filtered_df[filtered_df["Machine_Type"].isin(selected_types)]

    if selected_criticality:
        filtered_df = filtered_df[filtered_df["Criticality"].isin(selected_criticality)]

    if selected_risks:
        filtered_df = filtered_df[filtered_df["Risk_Level"].isin(selected_risks)]

    if search:
        search_mask = (
            filtered_df["Machine_ID"].str.contains(search, case=False, na=False)
            | filtered_df["Machine_Name"].str.contains(search, case=False, na=False)
            | filtered_df["Machine_Type"].str.contains(search, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]

    if filtered_df.empty:
        st.warning("No machine records match the selected dashboard filters.")
        st.stop()

    # ------------------------
    # Executive KPI cards
    # ------------------------
    total_machines = len(filtered_df)
    urgent_count = int((filtered_df["Risk_Level"] == "High Risk").sum())
    avg_availability = filtered_df["Availability"].mean()
    avg_mtbf = filtered_df["MTBF"].mean()
    total_downtime = filtered_df["Downtime_Hours"].sum()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        render_kpi_card(
            "Total Assets",
            f"{total_machines}",
            "Machines in current view",
            "#2463eb",
        )

    with kpi2:
        render_kpi_card(
            "Average Availability",
            f"{avg_availability:.2f}%",
            "Target: 95% or higher",
            "#0f9d76" if avg_availability >= 95 else "#f59e0b",
        )

    with kpi3:
        render_kpi_card(
            "Average MTBF",
            f"{avg_mtbf:.1f} h",
            "Higher means better reliability",
            "#7c3aed",
        )

    with kpi4:
        render_kpi_card(
            "Total Downtime",
            f"{total_downtime:.1f} h",
            "Accumulated downtime hours",
            "#f59e0b",
        )

    with kpi5:
        render_kpi_card(
            "Urgent Assets",
            f"{urgent_count}",
            "High-risk machines",
            "#dc2626",
        )

    st.write("")

    availability_gap = max(0, 95 - avg_availability)
    worst_machine = filtered_df.sort_values(
        by=["Risk_Level", "Downtime_Hours", "Failure_Count"],
        key=lambda series: series.map({"High Risk": 3, "Medium Risk": 2, "Low Risk": 1})
        if series.name == "Risk_Level" else series,
        ascending=False,
    ).iloc[0]

    if urgent_count > 0:
        insight_text = (
            f"<b>{urgent_count} machine(s) require urgent attention.</b> "
            f"The highest-priority asset is {worst_machine['Machine_ID']} - "
            f"{worst_machine['Machine_Name']}, with {worst_machine['Downtime_Hours']:.1f} "
            f"downtime hours and {worst_machine['Failure_Count']:.0f} recorded failures."
        )
    elif availability_gap > 0:
        insight_text = (
            f"No high-risk asset is detected, but average availability is "
            f"{availability_gap:.2f} percentage points below the 95% operational target."
        )
    else:
        insight_text = (
            "Current assets are within the acceptable operating range. "
            "Continue preventive maintenance and routine condition monitoring."
        )

    st.markdown(
        f'<div class="insight-box"><b>Management Insight:</b> {insight_text}</div>',
        unsafe_allow_html=True,
    )

    # ------------------------
    # Primary visual row
    # ------------------------
    risk_colors = {
        "High Risk": "#dc2626",
        "Medium Risk": "#f59e0b",
        "Low Risk": "#0f9d76",
    }

    visual_left, visual_right = st.columns([0.82, 1.55])

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
                    hole=0.62,
                    marker=dict(
                        colors=[risk_colors.get(level, "#94a3b8") for level in risk_count["Risk_Level"]],
                        line=dict(color="#ffffff", width=3),
                    ),
                    textinfo="label+value",
                    hovertemplate="%{label}: %{value} machine(s)<extra></extra>",
                )
            ]
        )
        fig_risk.add_annotation(
            text=f"<b>{total_machines}</b><br><span style='font-size:11px'>Assets</span>",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="#172033"),
        )
        fig_risk.update_layout(title="Risk Level Distribution")
        apply_powerbi_chart_layout(fig_risk, height=365, show_legend=False)
        st.plotly_chart(fig_risk, use_container_width=True, config={"displayModeBar": False})

    with visual_right:
        availability_chart_df = filtered_df.sort_values("Availability", ascending=True)
        fig_availability = px.bar(
            availability_chart_df,
            x="Availability",
            y="Machine_Name",
            orientation="h",
            color="Risk_Level",
            color_discrete_map=risk_colors,
            text="Availability",
            title="Asset Availability by Machine",
            hover_data={
                "Machine_ID": True,
                "Failure_Count": True,
                "Downtime_Hours": ":.1f",
                "Availability": ":.2f",
            },
        )
        fig_availability.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )
        fig_availability.add_vline(
            x=95,
            line_dash="dash",
            line_color="#64748b",
            annotation_text="95% target",
            annotation_position="top",
        )
        fig_availability.update_xaxes(range=[0, 103], title="Availability (%)")
        fig_availability.update_yaxes(title="")
        apply_powerbi_chart_layout(fig_availability, height=365, show_legend=True)
        st.plotly_chart(fig_availability, use_container_width=True, config={"displayModeBar": False})

    # ------------------------
    # Secondary visual row
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
            title="Failure Frequency vs Downtime",
            hover_data={
                "Operating_Hours": ":.0f",
                "Availability": ":.2f",
                "MTBF": ":.2f",
            },
            size_max=38,
        )
        fig_performance.update_traces(textposition="top center")
        fig_performance.update_xaxes(title="Failure Count")
        fig_performance.update_yaxes(title="Downtime Hours")
        apply_powerbi_chart_layout(fig_performance, height=370, show_legend=True)
        st.plotly_chart(fig_performance, use_container_width=True, config={"displayModeBar": False})

    with visual_bottom_right:
        maintenance_df = filtered_df.copy()
        maintenance_df["Next_Maintenance_Date"] = pd.to_datetime(
            maintenance_df["Next_Maintenance_Date"],
            errors="coerce",
        )
        maintenance_df["Days_To_Maintenance"] = (
            maintenance_df["Next_Maintenance_Date"] - pd.Timestamp(date.today())
        ).dt.days
        maintenance_df = maintenance_df.sort_values("Days_To_Maintenance").head(10)

        fig_schedule = px.bar(
            maintenance_df,
            x="Days_To_Maintenance",
            y="Machine_Name",
            orientation="h",
            color="Risk_Level",
            color_discrete_map=risk_colors,
            text="Days_To_Maintenance",
            title="Maintenance Timing: Top 10 Assets",
            hover_data={
                "Machine_ID": True,
                "Next_Maintenance_Date": "|%Y-%m-%d",
                "Maintenance_Priority": True,
            },
        )
        fig_schedule.update_traces(
            texttemplate="%{text} days",
            textposition="outside",
            cliponaxis=False,
        )
        fig_schedule.update_xaxes(title="Days remaining (negative values are overdue)")
        fig_schedule.update_yaxes(title="", categoryorder="total descending")
        apply_powerbi_chart_layout(fig_schedule, height=370, show_legend=True)
        st.plotly_chart(fig_schedule, use_container_width=True, config={"displayModeBar": False})

    # ------------------------
    # Priority table
    # ------------------------
    st.markdown('<div class="section-title">Asset Priority Register</div>', unsafe_allow_html=True)

    priority_order = {"High Risk": 3, "Medium Risk": 2, "Low Risk": 1}
    table_df = filtered_df.copy()
    table_df["Priority_Order"] = table_df["Risk_Level"].map(priority_order)
    table_df = table_df.sort_values(
        by=["Priority_Order", "Downtime_Hours", "Failure_Count"],
        ascending=[False, False, False],
    )

    table_df["Status"] = table_df["Risk_Level"].map(
        {
            "High Risk": "🔴 High Risk",
            "Medium Risk": "🟠 Medium Risk",
            "Low Risk": "🟢 Low Risk",
        }
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
    display_table["Next_Maintenance_Date"] = pd.to_datetime(
        display_table["Next_Maintenance_Date"],
        errors="coerce",
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Risk Status"),
            "Availability": st.column_config.ProgressColumn(
                "Availability",
                format="%.2f%%",
                min_value=0,
                max_value=100,
            ),
            "MTBF": st.column_config.NumberColumn("MTBF (hours)", format="%.2f"),
            "Failure_Count": st.column_config.NumberColumn("Failures", format="%d"),
            "Downtime_Hours": st.column_config.NumberColumn("Downtime (hours)", format="%.1f"),
            "Next_Maintenance_Date": st.column_config.DateColumn(
                "Next Maintenance",
                format="YYYY-MM-DD",
            ),
        },
    )

    csv = table_df.drop(columns=["Priority_Order"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Dashboard Data",
        data=csv,
        file_name="predictive_maintenance_dashboard.csv",
        mime="text/csv",
    )


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
