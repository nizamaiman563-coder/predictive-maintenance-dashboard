import os
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
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
    "Admin": "admin123",
    "Engineer": "engineer123",
    "Student": "student123",
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
# STREAMLIT PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    page_icon="🛠️",
    layout="wide"
)

check_login()
logout_button()

st.title("🛠️ AI-Driven Predictive Maintenance Scheduling System")
st.caption("Reliability Engineering Dashboard for Industrial Equipment Maintenance")


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


# ============================================================
# DASHBOARD MODULE
# ============================================================

if menu == "Dashboard":
    st.subheader("📋 Machine Reliability Overview")

    total_machines = len(df_result)
    high_risk = len(df_result[df_result["Risk_Level"] == "High Risk"])
    medium_risk = len(df_result[df_result["Risk_Level"] == "Medium Risk"])
    low_risk = len(df_result[df_result["Risk_Level"] == "Low Risk"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Machines", total_machines)
    col2.metric("High Risk Machines", high_risk)
    col3.metric("Medium Risk Machines", medium_risk)
    col4.metric("Low Risk Machines", low_risk)

    st.divider()

    search = st.text_input("🔍 Search machine by ID, name, or type")

    filtered_df = df_result.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["Machine_ID"].str.contains(search, case=False, na=False) |
            filtered_df["Machine_Name"].str.contains(search, case=False, na=False) |
            filtered_df["Machine_Type"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Dashboard Data as CSV",
        data=csv,
        file_name="predictive_maintenance_result.csv",
        mime="text/csv"
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
