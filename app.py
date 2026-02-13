import streamlit as st
import pandas as pd
from rapidfuzz import process
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key("1ZMCkVm2fM4-tRFb5rQiqY9fC8m6GPXzl-6fYtW3xfOU").sheet1


# =========================
# 🔐 AUTH CONFIG
# =========================

APP_USERS = {
    "aj": "covered",
    "dara": "covenant",
    "stacey": "psalms 91",
    "wendy": "amen", 
    "tameka": "favored"
}

# =========================
# 📂 DATA files
# =========================

FEELINGS_FILE = "feelings.csv"
VERSES_FILE = "verses.csv"
COVERINGS_FILE = "coverings.csv"
LOGS_FILE = "logs.csv"

# =========================
# 📊 LOAD DATA
# =========================

feelings_df = pd.read_csv(FEELINGS_FILE)
verses_df = pd.read_csv(VERSES_FILE)

# =========================
# 🔐 LOGIN SYSTEM
# =========================

def login():

    st.title("Our Daily Covering 🤍")
    st.markdown(
        "A private space where you're reminded daily "
        "that you're covered — in faith, strength, and love."
    )

    username_input = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Enter"):
        username = username_input.strip().lower()
        #st.write("You typed:", username_input)
        #st.write("You meant:", username)

        if username in APP_USERS and APP_USERS[username] == password:
            st.session_state["logged_in"] = True
            #store display version
            st.session_state["user"] = username_input
            st.success(f"Welcome, {username_input.title()} 🤍")
            st.write("PRESS ENTER TO CONTINUE")
        
        else:
            st.error("Access denied.")

if "logged_in" not in st.session_state:
    login()
    st.stop()

# =========================
# 🏠 APP HOME
# =========================

st.title("Our Daily Covering 🤍")


st.subheader("How are you feeling today?")

user_input = st.text_input(
    "Type how you feel…",
    placeholder="Overwhelmed, anxious, hopeful…"
)

# =========================
# 🔎 FUZZY FEELING MATCH
# =========================

if user_input:

    feeling_choices = feelings_df["Feeling"].tolist()

    matches = process.extract(
        user_input,
        feeling_choices,
        limit=5
    )

    st.write("Closest feelings:")

    selected_feeling = None

    for match in matches:
        feeling_name = match[0]
        score = match[1]

        if st.button(f"{feeling_name} ({score}%)"):
            selected_feeling = feeling_name
            st.session_state["selected_feeling"] = feeling_name

# =========================
# 📖 VERSE ENGINE
# =========================

if "selected_feeling" in st.session_state:

    feeling = st.session_state["selected_feeling"]

    theme = feelings_df.loc[
        feelings_df["Feeling"] == feeling,
        "Theme"
    ].values[0]

    st.subheader(f"Theme: {theme}")

    verse_matches = verses_df[
        verses_df["Theme"] == theme
    ].head(5)

    st.markdown("### Your Covering Options:")

    for i, row in verse_matches.iterrows():

        verse_label = f"{row['Book']} {row['Chapter']}:{row['Verse']}"

        with st.container():

            st.markdown(f"**{verse_label}**")
            st.write(row["Text"])

            if st.button(f"Add {verse_label}"):

                # =========================
                # 💌 SAVE TO GOOGLE SHEETS
                # =========================
                sheet.append_row([
                    st.session_state["user"],
                    str(datetime.now()),
                    feeling,
                    theme,
                    verse_label
                ])
                st.success("Added to Our Coverings 💌")
                
                
              
                # =========================
                # 🧠 SYSTEM LOG
                # =========================

                log_entry = {
                    "Timestamp": datetime.now(),
                    "User": st.session_state["user"],
                    "Input": user_input,
                    "Matched_Feeling": feeling,
                    "Selected_Verse": verse_label
                }

                pd.DataFrame([log_entry]).to_csv(
                    LOGS_FILE,
                    mode="a",
                    header=not os.path.exists(LOGS_FILE),
                    index=False
                )

                st.success("Added to Our Coverings 💌")
















