import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(page_title="Weight Loss Tracker", layout="wide")
st.write("App started successfully ✅")

# ------------------- SESSION INIT -------------------
if "logs" not in st.session_state:
    st.session_state.logs = []
if "settings" not in st.session_state:
    st.session_state.settings = {
        "height": 170,
        "weight": 70,
        "target_weight": 65,
        "target_date": datetime.date.today() + datetime.timedelta(days=30)
    }

# ------------------- BMR FUNCTION -------------------
def calculate_bmr(weight, height, age, gender="male"):
    if gender == "male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

# ------------------- DASHBOARD PAGE -------------------
def dashboard_page():
    st.markdown("<h2 class='title'>📊 Dashboard</h2>", unsafe_allow_html=True)
    settings = st.session_state.settings
    logs = st.session_state.logs

    if not logs:
        st.info("No logs yet. Please add some data in the Logging page.")
        return

    df = pd.DataFrame(logs)
    total_calories = df["calories"].sum()
    days_passed = (datetime.date.today() - df["date"].min()).days + 1
    avg_calories = total_calories / days_passed

    bmr = calculate_bmr(settings["weight"], settings["height"], 30, "male")

    st.metric("Average Calories Consumed", f"{avg_calories:.0f}")
    st.metric("BMR", f"{bmr:.0f}")

    # progress
    st.progress(min(avg_calories / bmr, 1.0))

    

# ------------------- LOGGING PAGE -------------------
def logging_page():
    st.markdown("<h2 class='title'>📝 Daily Logging</h2>", unsafe_allow_html=True)
    with st.form("log_form"):
        date = st.date_input("Date", datetime.date.today())
        calories = st.number_input("Calories Consumed", 0, 10000, 2000)
        submitted = st.form_submit_button("Save")
        if submitted:
            st.session_state.logs.append({"date": date, "calories": calories})
            st.success("Log saved!")

# ------------------- SETTINGS PAGE -------------------
def settings_page():
    st.markdown("<h2 class='title'>⚙️ Settings</h2>", unsafe_allow_html=True)
    with st.form("settings_form"):
        height = st.number_input("Height (cm)", 100, 250, st.session_state.settings["height"])
        weight = st.number_input("Current Weight (kg)", 30, 200, st.session_state.settings["weight"])
        target_weight = st.number_input("Target Weight (kg)", 30, 200, st.session_state.settings["target_weight"])
        target_date = st.date_input("Target Date", st.session_state.settings["target_date"])
        submitted = st.form_submit_button("Save Settings")
        if submitted:
            st.session_state.settings.update({
                "height": height,
                "weight": weight,
                "target_weight": target_weight,
                "target_date": target_date
            })
            st.success("Settings updated!")

# ------------------- TRENDS PAGE -------------------
def trends_page():
    st.markdown("<h2 class='title'>📈 Trends</h2>", unsafe_allow_html=True)
    if not st.session_state.logs:
        st.info("No data yet. Please log some entries first.")
        return

    df = pd.DataFrame(st.session_state.logs)
    df = df.sort_values("date")

    fig, ax = plt.subplots()
    ax.plot(df["date"], df["calories"], marker="o")
    ax.axhline(calculate_bmr(st.session_state.settings["weight"], st.session_state.settings["height"], 30), color="red", linestyle="--", label="BMR")
    ax.set_title("Calories vs Date")
    ax.set_ylabel("Calories")
    ax.legend()
    st.pyplot(fig)

def local_css(file_name="style.css"):
    try:
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {file_name} — continuing without custom styles.")

# now you can call without args
local_css()

# ------------------- MAIN -------------------
def main():
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Trends", "Logging", "Settings"])

    if page == "Dashboard":
        dashboard_page()
    elif page == "Trends":
        trends_page()
    elif page == "Logging":
        logging_page()
    elif page == "Settings":
        settings_page()

if __name__ == "__main__":
    local_css()
    main()
