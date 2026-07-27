POWER BI-STYLE PREDICTIVE MAINTENANCE DASHBOARD

Files
- predictive_maintenance_powerbi_dashboard.py
- requirements_dashboard.txt

How to run on Windows
1. Place the Python file in your project folder.
2. Open Command Prompt or PowerShell in that folder.
3. Install dependencies:
   pip install -r requirements_dashboard.txt
4. Start the application:
   streamlit run predictive_maintenance_powerbi_dashboard.py

The application automatically creates machine_data.csv if it is not already present.

Default login examples
- Admin_Nizam / nizam123
- Engineer_Naim / naim123

Main dashboard improvements
- Power BI-style executive header and visual theme
- Interactive filters for machine type, criticality, risk, and search
- KPI cards for assets, availability, MTBF, downtime, and urgent machines
- Risk distribution donut chart
- Availability-by-machine chart with 95% target line
- Failure-versus-downtime bubble chart
- Upcoming/overdue maintenance chart
- Priority register with availability progress bars
- Filtered CSV download
