import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# --- MongoDB Connection ---
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["happy_quotes_db"]

# --- Helper: log activity ---
def log_activity(user_email, action, details=""):
    """Log user actions in MongoDB."""
    db.user_activity.insert_one({
        "user_email": user_email,
        "action": action,
        "details": details,
        "timestamp": datetime.now()
    })

# --- Helper: fetch activity ---
def get_user_activity(user_email=None):
    """Return a DataFrame of activity for a specific user or all users."""
    query = {"user_email": user_email} if user_email else {}
    data = list(db.user_activity.find(query, {"_id": 0}))
    df = pd.DataFrame(data)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df if not df.empty else pd.DataFrame(columns=["user_email", "action", "details", "timestamp"])

# --- DASHBOARD UI ---
def dashboard_view(current_user=None):
    st.set_page_config(page_title="📊 User Dashboard", layout="wide")
    st.title("📊 User Activity Dashboard")

    # Show current user info
    if current_user:
        user_email = current_user.get("email", "guest")
        st.subheader(f"Hello, {current_user.get('first_name', 'Guest')} ({user_email})")
    else:
        user_email = None
        st.info("Showing global activity. Log in to see your personal activity.")

    # Log example activity (optional)
    if st.button("Log a random action", key="log_random_action"):
        if current_user:
            log_activity(user_email, "viewed_quote", "User viewed a happy quote 😊")
            st.success("Activity logged!")
        else:
            st.warning("Please log in to record activity.")

    # Show activity table
    st.subheader("📄 Activity History")
    activity_df = get_user_activity(user_email)
    if not activity_df.empty:
        st.dataframe(activity_df.sort_values("timestamp", ascending=False))

        # Timeline chart
        st.subheader("📈 Activity Over Time")
        timeline = activity_df.groupby(activity_df["timestamp"].dt.date).size()
        st.line_chart(timeline)

        # Action distribution chart
        st.subheader("📊 Action Breakdown")
        action_counts = activity_df["action"].value_counts()
        st.bar_chart(action_counts)
    else:
        st.info("No activity logged yet.")

    # Admin: show all users
    st.markdown("---")
    if st.checkbox("Show all users' activity", key="show_all_activity"):
        all_df = get_user_activity()
        if not all_df.empty:
            st.dataframe(all_df.sort_values("timestamp", ascending=False))
        else:
            st.info("No activity found.")
