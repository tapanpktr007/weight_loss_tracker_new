import streamlit as st

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date, datetime
from google.oauth2.service_account import Credentials

creds_dict = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(creds_dict)
gc = gspread.authorize(credentials)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
# -------------------
# Google Sheets Setup
# -------------------
SHEETS = {
    "daily_logs": ["Date", "Calories", "Steps", "Weight", "Notes"],
    "settings": ["Setting", "Value"],
    "trends": ["Date", "Net Calories", "Weight", "Steps"]
}

import gspread
from google.oauth2 import service_account

def connect_gsheet(sheet_name):
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],  # <-- use secrets
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)
    return client.open(sheet_name)


def ensure_worksheets(sheet_name="Fitness_Tracker_Data"):
    spreadsheet = connect_gsheet(sheet_name)
    existing_titles = [ws.title for ws in spreadsheet.worksheets()]
    for title, headers in SHEETS.items():
        if title not in existing_titles:
            ws = spreadsheet.add_worksheet(title=title, rows=1000, cols=len(headers))
            ws.append_row(headers)
        else:
            ws = spreadsheet.worksheet(title)
            if len(ws.get_all_values()) == 0:
                ws.append_row(headers)
    return spreadsheet

spreadsheet = ensure_worksheets("Fitness_Tracker_Data")

# -------------------
# Helpers
# -------------------
def add_daily_log(date_str, calories, steps, weight, notes=""):
    ws = spreadsheet.worksheet("daily_logs")
    headers = ["Date", "Calories", "Steps", "Weight", "Notes"]

    # Add headers if sheet empty
    if len(ws.get_all_values()) == 0:
        ws.append_row(headers)

    # Read records safely
    records = ws.get_all_records(expected_headers=headers)
    date_exists = False
    for idx, record in enumerate(records, start=2):
        if record["Date"] == date_str:
            ws.update(f"A{idx}:E{idx}", [[date_str, calories, steps, weight, notes]])
            date_exists = True
            break

    if not date_exists:
        ws.append_row([date_str, calories, steps, weight, notes])

def get_daily_logs():
    ws = spreadsheet.worksheet("daily_logs")
    df = pd.DataFrame(ws.get_all_records())
    if not df.empty:
        df.columns = SHEETS["daily_logs"]  # standardize columns
    return df

def get_settings():
    ws = spreadsheet.worksheet("settings")
    rows = ws.get_all_records()
    settings = {row['Setting']: row['Value'] for row in rows}
    return settings

def update_setting(key, value):
    ws = spreadsheet.worksheet("settings")
    records = ws.get_all_records()
    found = False
    for idx, r in enumerate(records, start=2):
        if r["Setting"] == key:
            ws.update_cell(idx, 2, str(value))
            found = True
            break
    if not found:
        ws.append_row([key, str(value)])

# -------------------
# Streamlit UI
# -------------------
st.set_page_config(page_title="Weight Loss Tracker", layout="wide")
page = st.sidebar.radio("Navigate", ["Daily Logging", "Settings", "Dashboard"])

# -------------------
# Daily Logging
# -------------------
if page == "Daily Logging":
    st.header("📅 Daily Log")
    with st.form("daily_log_form"):
        log_date = st.date_input("Date", value=date.today())
        calories = st.number_input("Calories Consumed", min_value=0, step=50)
        steps = st.number_input("Steps Taken", min_value=0, step=100)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
        notes = st.text_area("Notes", "")
        submitted = st.form_submit_button("Save Log")
        if submitted:
            add_daily_log(str(log_date), calories, steps, weight, notes)
            st.success("✅ Log saved!")

# -------------------
# Settings Page
# -------------------
elif page == "Settings":
    st.header("⚙️ Profile & Goals")
    settings = get_settings()
    
    height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=float(settings.get("Height", 170.0)))
    weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=300.0, value=float(settings.get("Weight", 70.0)))
    target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=300.0, value=float(settings.get("Target Weight", 65.0)))
    target_date = st.date_input("Target Date", value=datetime.strptime(settings.get("Target Date", str(date.today())), "%Y-%m-%d").date())

    if st.button("Save Settings"):
        update_setting("Height", height)
        update_setting("Weight", weight)
        update_setting("Target Weight", target_weight)
        update_setting("Target Date", str(target_date))
        st.success("✅ Settings saved!")

# -------------------
# Dashboard Page
# -------------------
elif page == "Dashboard":
    st.header("📊 Progress Dashboard")
    df_logs = get_daily_logs()
    settings = get_settings()

    if df_logs.empty:
        st.info("No daily logs yet. Add entries from the Daily Logging page.")
    else:
        # Convert Date
        df_logs["Date"] = pd.to_datetime(df_logs["Date"])
        df_logs = df_logs.sort_values("Date")

        # Simplified net calories (for now)
        df_logs["Net Calories"] = df_logs["Calories"]  # can subtract BMR / burn later

        # Latest logs table
        st.subheader("Latest Logs")
        st.dataframe(df_logs.tail(5))

        # Trends
        st.subheader("Weight & Steps Trend")
        st.line_chart(df_logs.set_index("Date")[["Weight", "Steps"]])

        st.subheader("Calories Trend")
        st.line_chart(df_logs.set_index("Date")[["Calories", "Net Calories"]])

        # Progress towards target weight
        current_weight = float(df_logs["Weight"].iloc[-1])
        target_weight = float(settings.get("Target Weight", current_weight))
        start_weight = float(settings.get("Weight", current_weight))
        progress_pct = round((start_weight - current_weight) / max(start_weight - target_weight, 1e-5) * 100, 1)
        st.metric("Progress to Target Weight", f"{progress_pct}%")
