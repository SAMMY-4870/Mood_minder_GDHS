import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pymongo import MongoClient
from datetime import datetime, timedelta
import numpy as np

# --- MongoDB Connection ---
MONGO_URI = "mongodb+srv://Samarth_90:Samarth%409090@moodminder.dci9zcf.mongodb.net/?retryWrites=true&w=majority"
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

# --- ANALYTICS HELPERS ---
def get_focus_analytics(user_email, days=30):
    """Get focus level analytics for the user"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get game sessions with focus scores
    sessions = list(db.game_sessions.find({
        "user_email": user_email,
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }).sort("timestamp", 1))
    
    if not sessions:
        return None
    
    # Process focus scores over time
    focus_data = []
    for session in sessions:
        focus_score = session.get("session_data", {}).get("focus_score", 0)
        focus_data.append({
            "date": session["timestamp"].date(),
            "focus_score": focus_score,
            "game": session["game"],
            "timestamp": session["timestamp"]
        })
    
    return pd.DataFrame(focus_data)

def get_performance_metrics(user_email):
    """Get comprehensive performance metrics"""
    # Game performance
    game_stats = {}
    games = ["breathing", "memory", "reaction", "puzzle", "rps", "guess", "trivia"]
    
    for game in games:
        stats = db.game_scores.find_one({"email": user_email, "game": game})
        if stats:
            game_stats[game] = stats
    
    # Focus trends
    focus_df = get_focus_analytics(user_email, 30)
    
    # Activity patterns
    activity_df = get_user_activity(user_email)
    
    return {
        "game_stats": game_stats,
        "focus_data": focus_df,
        "activity_data": activity_df
    }

def calculate_insights(metrics):
    """Calculate insights and recommendations"""
    insights = []
    
    # Focus level insights
    if metrics["focus_data"] is not None and not metrics["focus_data"].empty:
        avg_focus = metrics["focus_data"]["focus_score"].mean()
        if avg_focus >= 80:
            insights.append("🎯 Excellent focus levels! You're performing very well.")
        elif avg_focus >= 60:
            insights.append("📈 Good focus levels. Keep up the great work!")
        else:
            insights.append("💡 Consider taking breaks and practicing breathing exercises.")
    
    # Game performance insights
    game_stats = metrics["game_stats"]
    if game_stats:
        most_played = max(game_stats.keys(), key=lambda k: game_stats[k].get("games_played", 0))
        insights.append(f"🎮 Your most played game is {most_played.title()}")
        
        # Check for improvement opportunities
        if "memory" in game_stats and game_stats["memory"].get("pairs_found", 0) < 20:
            insights.append("🧠 Try playing more memory games to improve cognitive function.")
        
        if "reaction" in game_stats and game_stats["reaction"].get("best_time", 1000) > 500:
            insights.append("⚡ Practice reaction time games to improve focus and reflexes.")
    
    return insights

# --- DASHBOARD UI ---
def dashboard_view(current_user=None):
    st.set_page_config(page_title="📊 Mental Health Dashboard", layout="wide")
    
    # Header
    st.title("📊 Mental Health & Focus Dashboard")
    
    if not current_user:
        st.warning("Please log in to view your personalized dashboard.")
        return
    
    user_email = current_user.get("email")
    user_name = current_user.get("first_name", "User")
    
    # Welcome message
    st.success(f"Welcome back, {user_name}! Here's your mental health journey overview.")
    
    # Get metrics
    with st.spinner("Loading your data..."):
        metrics = get_performance_metrics(user_email)
    
    # Key Metrics Row
    st.subheader("🎯 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sessions = sum(stats.get("games_played", 0) for stats in metrics["game_stats"].values())
        st.metric("Total Sessions", total_sessions)
    
    with col2:
        if metrics["focus_data"] is not None and not metrics["focus_data"].empty:
            avg_focus = metrics["focus_data"]["focus_score"].mean()
            st.metric("Avg Focus Score", f"{avg_focus:.1f}%")
        else:
            st.metric("Avg Focus Score", "N/A")
    
    with col3:
        if metrics["activity_data"] is not None and not metrics["activity_data"].empty:
            recent_activity = len(metrics["activity_data"][metrics["activity_data"]["timestamp"] >= datetime.utcnow() - timedelta(days=7)])
            st.metric("This Week's Activity", recent_activity)
        else:
            st.metric("This Week's Activity", "0")
    
    with col4:
        if metrics["game_stats"]:
            best_game = max(metrics["game_stats"].keys(), key=lambda k: metrics["game_stats"][k].get("wins", 0) + metrics["game_stats"][k].get("correct", 0))
            st.metric("Best Game", best_game.title())
        else:
            st.metric("Best Game", "N/A")
    
    # Focus Level Trends
    st.subheader("📈 Focus Level Trends")
    if metrics["focus_data"] is not None and not metrics["focus_data"].empty:
        # Daily focus scores
        daily_focus = metrics["focus_data"].groupby("date")["focus_score"].mean().reset_index()
        
        fig = px.line(daily_focus, x="date", y="focus_score", 
                     title="Daily Focus Score Trend",
                     labels={"focus_score": "Focus Score (%)", "date": "Date"})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Focus by game type
        game_focus = metrics["focus_data"].groupby("game")["focus_score"].mean().reset_index()
        fig2 = px.bar(game_focus, x="game", y="focus_score",
                     title="Average Focus Score by Game",
                     labels={"focus_score": "Focus Score (%)", "game": "Game"})
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No focus data available. Start playing games to see your focus trends!")
    
    # Game Performance
    st.subheader("🎮 Game Performance")
    if metrics["game_stats"]:
        # Create performance comparison
        game_data = []
        for game, stats in metrics["game_stats"].items():
            game_data.append({
                "Game": game.title(),
                "Sessions": stats.get("games_played", 0),
                "Wins": stats.get("wins", 0) + stats.get("correct", 0),
                "Total Score": stats.get("total_cycles", 0) + stats.get("pairs_found", 0) + stats.get("wins", 0)
            })
        
        game_df = pd.DataFrame(game_data)
        
        # Sessions chart
        fig3 = px.bar(game_df, x="Game", y="Sessions", title="Sessions Played by Game")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Performance table
        st.dataframe(game_df, use_container_width=True)
    else:
        st.info("No game performance data available. Start playing games to track your progress!")
    
    # Activity Timeline
    st.subheader("📅 Activity Timeline")
    if metrics["activity_data"] is not None and not metrics["activity_data"].empty:
        # Recent activity
        recent_activity = metrics["activity_data"].tail(20)
        st.dataframe(recent_activity[["timestamp", "action", "details"]], use_container_width=True)
        
        # Activity distribution
        activity_counts = metrics["activity_data"]["action"].value_counts().reset_index()
        activity_counts.columns = ["Action", "Count"]
        
        fig4 = px.pie(activity_counts, values="Count", names="Action", title="Activity Distribution")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No activity data available.")
    
    # Insights and Recommendations
    st.subheader("💡 Insights & Recommendations")
    insights = calculate_insights(metrics)
    
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info("Keep playing games and engaging with the platform to get personalized insights!")
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎮 Play Games", use_container_width=True):
            st.switch_page("pages/games.py")
    
    with col2:
        if st.button("🌬️ Breathing Exercise", use_container_width=True):
            st.switch_page("pages/breathing.py")
    
    with col3:
        if st.button("📊 View Leaderboard", use_container_width=True):
            st.switch_page("pages/leaderboard.py")
