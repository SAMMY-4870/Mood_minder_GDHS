"""
Progress Notifications and Motivational Features
"""
from datetime import datetime, timedelta
from pymongo import MongoClient
import random

# MongoDB Connection
MONGO_URI = "mongodb+srv://Samarth_90:Samarth%409090@moodminder.dci9zcf.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["happy_quotes_db"]

# Motivational quotes and messages
MOTIVATIONAL_QUOTES = [
    "🌟 Great job! Your focus is improving with each session.",
    "🎯 You're on fire! Keep up the excellent work.",
    "💪 Consistency is key! You're building great habits.",
    "🧠 Your brain is getting stronger every day!",
    "⚡ Amazing reflexes! Your reaction time is improving.",
    "🎮 You're becoming a mental health champion!",
    "🌈 Every game session brings you closer to your goals.",
    "✨ Your dedication to mental wellness is inspiring!",
    "🏆 You're setting new personal records!",
    "🎉 Progress, not perfection! You're doing great."
]

ACHIEVEMENT_MESSAGES = {
    "first_session": "🎉 Congratulations! You completed your first game session!",
    "focus_master": "🎯 Focus Master! You achieved 80%+ focus in 5 consecutive sessions!",
    "memory_champion": "🧠 Memory Champion! You found 50+ pairs in memory games!",
    "reaction_legend": "⚡ Lightning Fast! Your reaction time is under 200ms!",
    "puzzle_master": "🧩 Puzzle Master! You solved 20+ puzzles!",
    "streak_warrior": "🔥 Streak Warrior! You've played for 7 days in a row!",
    "zen_master": "🌬️ Zen Master! You completed 100+ breathing cycles!",
    "consistency_king": "👑 Consistency King! You've been active for 30 days!",
    "improvement_hero": "📈 Improvement Hero! You improved your focus by 20% this week!",
    "wellness_warrior": "🛡️ Wellness Warrior! You're prioritizing your mental health!"
}

def check_achievements(user_email):
    """Check for new achievements and return notifications"""
    notifications = []
    
    # Get user's game stats
    game_stats = {}
    games = ["breathing", "memory", "reaction", "puzzle", "rps", "guess", "trivia"]
    
    for game in games:
        stats = db.game_scores.find_one({"email": user_email, "game": game})
        if stats:
            game_stats[game] = stats
    
    # Check for first session
    total_sessions = sum(stats.get("games_played", 0) for stats in game_stats.values())
    if total_sessions == 1:
        notifications.append({
            "type": "achievement",
            "title": "First Steps!",
            "message": ACHIEVEMENT_MESSAGES["first_session"],
            "icon": "🎉",
            "timestamp": datetime.utcnow()
        })
    
    # Check for focus master (80%+ focus in 5 consecutive sessions)
    recent_sessions = list(db.game_sessions.find({
        "user_email": user_email,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
    }).sort("timestamp", -1).limit(5))
    
    if len(recent_sessions) >= 5:
        focus_scores = [s.get("session_data", {}).get("focus_score", 0) for s in recent_sessions]
        if all(score >= 80 for score in focus_scores):
            notifications.append({
                "type": "achievement",
                "title": "Focus Master!",
                "message": ACHIEVEMENT_MESSAGES["focus_master"],
                "icon": "🎯",
                "timestamp": datetime.utcnow()
            })
    
    # Check for memory champion
    if "memory" in game_stats and game_stats["memory"].get("pairs_found", 0) >= 50:
        notifications.append({
            "type": "achievement",
            "title": "Memory Champion!",
            "message": ACHIEVEMENT_MESSAGES["memory_champion"],
            "icon": "🧠",
            "timestamp": datetime.utcnow()
        })
    
    # Check for reaction legend
    if "reaction" in game_stats and game_stats["reaction"].get("best_time", 1000) < 200:
        notifications.append({
            "type": "achievement",
            "title": "Lightning Fast!",
            "message": ACHIEVEMENT_MESSAGES["reaction_legend"],
            "icon": "⚡",
            "timestamp": datetime.utcnow()
        })
    
    # Check for puzzle master
    if "puzzle" in game_stats and game_stats["puzzle"].get("puzzles_completed", 0) >= 20:
        notifications.append({
            "type": "achievement",
            "title": "Puzzle Master!",
            "message": ACHIEVEMENT_MESSAGES["puzzle_master"],
            "icon": "🧩",
            "timestamp": datetime.utcnow()
        })
    
    # Check for zen master
    if "breathing" in game_stats and game_stats["breathing"].get("total_cycles", 0) >= 100:
        notifications.append({
            "type": "achievement",
            "title": "Zen Master!",
            "message": ACHIEVEMENT_MESSAGES["zen_master"],
            "icon": "🌬️",
            "timestamp": datetime.utcnow()
        })
    
    # Check for streak warrior (7 days in a row)
    activity_data = list(db.user_activity.find({
        "user_email": user_email,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
    }).sort("timestamp", 1))
    
    if activity_data:
        # Group by date
        daily_activity = {}
        for activity in activity_data:
            date = activity["timestamp"].date()
            if date not in daily_activity:
                daily_activity[date] = []
            daily_activity[date].append(activity)
        
        # Check for 7 consecutive days
        if len(daily_activity) >= 7:
            notifications.append({
                "type": "achievement",
                "title": "Streak Warrior!",
                "message": ACHIEVEMENT_MESSAGES["streak_warrior"],
                "icon": "🔥",
                "timestamp": datetime.utcnow()
            })
    
    return notifications

def get_motivational_message(user_email):
    """Get a random motivational message"""
    return random.choice(MOTIVATIONAL_QUOTES)

def get_progress_insights(user_email):
    """Get personalized progress insights"""
    insights = []
    
    # Get recent focus data
    recent_sessions = list(db.game_sessions.find({
        "user_email": user_email,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
    }).sort("timestamp", 1))
    
    if recent_sessions:
        focus_scores = [s.get("session_data", {}).get("focus_score", 0) for s in recent_sessions]
        avg_focus = sum(focus_scores) / len(focus_scores)
        
        if avg_focus >= 80:
            insights.append("🎯 Your focus levels are excellent! You're performing at your best.")
        elif avg_focus >= 60:
            insights.append("📈 Good focus levels! Keep practicing to reach even higher scores.")
        else:
            insights.append("💡 Consider taking breaks between sessions to improve focus.")
        
        # Check for improvement trend
        if len(focus_scores) >= 3:
            recent_avg = sum(focus_scores[-3:]) / 3
            earlier_avg = sum(focus_scores[:-3]) / len(focus_scores[:-3]) if len(focus_scores) > 3 else recent_avg
            
            if recent_avg > earlier_avg + 10:
                insights.append("📈 Great improvement! Your focus is getting better with practice!")
            elif recent_avg < earlier_avg - 10:
                insights.append("💪 Don't worry! Focus can vary. Try different games to find what works best.")
    
    # Get game performance insights
    game_stats = {}
    games = ["breathing", "memory", "reaction", "puzzle", "rps", "guess", "trivia"]
    
    for game in games:
        stats = db.game_scores.find_one({"email": user_email, "game": game})
        if stats:
            game_stats[game] = stats
    
    if game_stats:
        most_played = max(game_stats.keys(), key=lambda k: game_stats[k].get("games_played", 0))
        insights.append(f"🎮 Your favorite game is {most_played.title()}. Try exploring other games for variety!")
        
        # Check for specific improvements
        if "memory" in game_stats:
            pairs_found = game_stats["memory"].get("pairs_found", 0)
            if pairs_found > 0:
                insights.append(f"🧠 You've found {pairs_found} memory pairs! Your cognitive skills are improving.")
        
        if "reaction" in game_stats:
            best_time = game_stats["reaction"].get("best_time", 0)
            if best_time > 0:
                insights.append(f"⚡ Your best reaction time is {best_time/1000:.2f}s! Keep practicing to get even faster.")
    
    return insights

def save_notification(user_email, notification):
    """Save notification to database"""
    db.notifications.insert_one({
        "user_email": user_email,
        "type": notification["type"],
        "title": notification["title"],
        "message": notification["message"],
        "icon": notification["icon"],
        "timestamp": notification["timestamp"],
        "read": False
    })

def get_user_notifications(user_email, limit=10):
    """Get user's notifications"""
    notifications = list(db.notifications.find({
        "user_email": user_email
    }).sort("timestamp", -1).limit(limit))
    
    return notifications

def mark_notification_read(notification_id):
    """Mark notification as read"""
    db.notifications.update_one(
        {"_id": notification_id},
        {"$set": {"read": True}}
    )

def get_weekly_progress_summary(user_email):
    """Get weekly progress summary"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # Get sessions this week
    sessions = list(db.game_sessions.find({
        "user_email": user_email,
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }))
    
    # Get activity this week
    activities = list(db.user_activity.find({
        "user_email": user_email,
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }))
    
    summary = {
        "sessions_completed": len(sessions),
        "activities_logged": len(activities),
        "focus_scores": [s.get("session_data", {}).get("focus_score", 0) for s in sessions],
        "games_played": len(set(s["game"] for s in sessions)),
        "improvement_trend": "up" if len(sessions) > 0 else "neutral"
    }
    
    if summary["focus_scores"]:
        summary["avg_focus"] = sum(summary["focus_scores"]) / len(summary["focus_scores"])
    else:
        summary["avg_focus"] = 0
    
    return summary
