# Set environment variables before any imports to prevent TensorFlow issues
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, send_file, flash, jsonify
from pymongo import MongoClient
import random
import secrets
from datetime import datetime, timedelta
import re
from src.recommender import build_advanced_suggestions
from src.notifications import check_achievements, get_motivational_message, get_progress_insights, save_notification, get_user_notifications, get_weekly_progress_summary
from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
from src.gemini_chatbot import health_chatbot
# Keep a minimal safety note for user protection
SUPPORT_DISCLAIMER = (
    "If you’re in immediate danger or considering self-harm, call local emergency services or 988 (U.S.)."
)



# --- CONFIG ---
IMAGES_FOLDER = os.path.join("data", "images", "happy")
MUSIC_FOLDER = os.path.join("data", "music")
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
BG_IMAGE_PATH = os.environ.get("BG_IMAGE_PATH", r"C:\\Project\\happy_quotes_ml_project\\data\\images\\meditation.jpg")

# --- APP INIT ---
app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- DB ---
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://Samarth_90:Samarth%409090@moodminder.dci9zcf.mongodb.net/?retryWrites=true&w=majority"
)
client = MongoClient(MONGO_URI)
db = client["happy_quotes_db"]
# --- GLOBAL TEMPLATE CONTEXT ---
@app.context_processor
def inject_user_context():
    # Make `user` available in all templates so navbar state updates immediately after login/logout
    return {"user": get_current_user()}



# --- HELPERS ---
def get_current_user():
    email = session.get("user_email")
    if not email:
        return None
    try:
        user = db.users.find_one({"email": email}, {"_id": 0, "password": 0})
        return user
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def require_login():
    email = session.get("user_email")
    if not email:
        flash("Please login to access this page.", "warning")
        return False
    
    # Verify user still exists in database
    try:
        user = db.users.find_one({"email": email})
        if not user:
            session.pop("user_email", None)  # Clear invalid session
            flash("Your session has expired. Please login again.", "warning")
            return False
        return True
    except Exception as e:
        flash(f"Database connection error: {str(e)}", "danger")
        print(f"Database error in require_login: {e}")
        return False


# --- GAME SCORE HELPERS ---
def _update_game_score(email: str, game: str, inc: dict, set_min: dict | None = None):
    if not email:
        return
    update_doc = {"$inc": inc, "$set": {"updated_at": datetime.utcnow()}}
    if set_min:
        update_doc["$min"] = set_min
    db.game_scores.update_one(
        {"email": email, "game": game},
        update_doc,
        upsert=True,
    )

def _log_game_session(email: str, game: str, session_data: dict):
    """Log detailed game session data for analytics"""
    if not email:
        return
    
    session_record = {
        "user_email": email,
        "game": game,
        "timestamp": datetime.utcnow(),
        "session_data": session_data
    }
    db.game_sessions.insert_one(session_record)

def _calculate_focus_score(session_data: dict) -> float:
    """Calculate focus score based on game performance metrics"""
    # Focus score calculation based on accuracy, reaction time, and consistency
    accuracy = session_data.get('accuracy', 0)
    reaction_time = session_data.get('avg_reaction_time', 1000)  # in ms
    consistency = session_data.get('consistency', 0)
    
    # Normalize reaction time (lower is better, max 2000ms)
    reaction_score = max(0, (2000 - reaction_time) / 2000)
    
    # Weighted focus score (0-100)
    focus_score = (accuracy * 0.4 + reaction_score * 0.3 + consistency * 0.3) * 100
    return round(focus_score, 2)


def _get_user_game_stats(email: str, game: str) -> dict:
    if not email:
        return {}
    doc = db.game_scores.find_one({"email": email, "game": game}, {"_id": 0})
    return doc or {}


def _get_leaderboard(game: str, sort_field: str, limit: int = 5):
    cursor = db.game_scores.find({"game": game}).sort(sort_field, -1).limit(limit)
    return list(cursor)


# --- ACTIVITY LOGGING ---
def log_activity(user_email: str | None, action: str, details: str = ""):
    if not user_email:
        return
    db.user_activity.insert_one({
        "user_email": user_email,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow(),
    })


_TOKEN_SPLIT = re.compile(r"[^a-zA-Z0-9]+")


def _simple_tokens(text: str) -> list[str]:
    return [t for t in _TOKEN_SPLIT.split((text or "").lower()) if t]


def get_user_interests(email: str | None, limit: int = 200) -> dict:
    if not email:
        return {"counts": {}, "tokens": {}}
    cursor = db.user_activity.find({"user_email": email}).sort("timestamp", -1).limit(limit)
    counts = {"quotes": 0, "images": 0, "music": 0, "games": 0}
    tokens: dict[str, int] = {}
    for doc in cursor:
        action = (doc.get("action") or "").lower()
        details = doc.get("details") or ""
        text = f"{action} {details}"
        for tok in _simple_tokens(text):
            tokens[tok] = tokens.get(tok, 0) + 1
        if "quote" in action:
            counts["quotes"] += 1
        if "image" in action:
            counts["images"] += 1
        if "song" in action or "music" in action:
            counts["music"] += 1
        if "game" in action or action in ("rps_win", "rps_loss", "rps_draw", "trivia_correct", "trivia_incorrect"):
            counts["games"] += 1
    return {"counts": counts, "tokens": tokens}


def build_suggestions(interests: dict) -> list[dict]:
    counts = interests.get("counts", {})
    tokens = interests.get("tokens", {})
    suggestions: list[dict] = []
    # Determine dominant area
    area = None
    if counts:
        area = max(counts, key=lambda k: counts.get(k, 0))
    # Map areas to learning suggestions
    if area == "quotes":
        suggestions.append({"text": "Explore Transformers for text (BERT/GPT)", "url": url_for("quotes")})
        suggestions.append({"text": "Try a new quote now", "url": url_for("quotes")})
    elif area == "music":
        suggestions.append({"text": "Deep Recommenders for music discovery", "url": url_for("music")})
        suggestions.append({"text": "Play a random happy song", "url": url_for("music")})
    elif area == "images":
        suggestions.append({"text": "CNNs & Vision Transformers for images", "url": url_for("images")})
        suggestions.append({"text": "See a happy image", "url": url_for("images")})
    elif area == "games":
        suggestions.append({"text": "Reinforcement Learning basics via mini games", "url": url_for("games")})
        suggestions.append({"text": "Play Rock–Paper–Scissors", "url": url_for("game_rps")})
    else:
        suggestions.append({"text": "Try a daily quote", "url": url_for("quotes")})
        suggestions.append({"text": "Play a relaxing song", "url": url_for("music")})

    # Token-based nudges
    if tokens.get("upload", 0) > 0:
        suggestions.append({"text": "Add more content you love", "url": url_for("upload")})
    if tokens.get("trivia", 0) > 1:
        suggestions.append({"text": "Boost your brain with a trivia round", "url": url_for("game_trivia")})
    if tokens.get("image", 0) > 1:
        suggestions.append({"text": "Curate your happy gallery", "url": url_for("images")})
    return suggestions[:4]


# --- ROUTES ---
@app.route("/")
def home():
    user = get_current_user()
    suggestions = []
    notifications = []
    progress_insights = []
    motivational_message = ""
    
    if user:
        # Try advanced recommender first; fall back to heuristic suggestions
        try:
            advanced = build_advanced_suggestions(db, user.get("email"), url_for)
        except Exception:
            advanced = []
        if advanced:
            suggestions = advanced
        else:
            interests = get_user_interests(user.get("email"))
            suggestions = build_suggestions(interests)
        
        # Get notifications and insights
        try:
            notifications = check_achievements(user.get("email"))
            progress_insights = get_progress_insights(user.get("email"))
            motivational_message = get_motivational_message(user.get("email"))
            
            # Save new notifications
            for notification in notifications:
                save_notification(user.get("email"), notification)
        except Exception as e:
            print(f"Error loading notifications: {e}")

    theme = {
        "brand": "#6f42c1",
        "brand2": "#20c997",
        "brand3": "#ff6b6b",
        "brand4": "#feca57",
    }

    return render_template("home.html", user=user, suggestions=suggestions, theme=theme, 
                          notifications=notifications, progress_insights=progress_insights, 
                          motivational_message=motivational_message)



@app.route("/quotes", methods=["GET", "POST"])
def quotes():
    user = get_current_user()
    random_quote = None
    if request.method == "POST" and request.form.get("action") == "random":
        quotes_list = list(db.quotes.find({}, {"_id": 0}))
        if quotes_list:
            random_quote = random.choice(quotes_list)
            if user:
                log_activity(user.get("email"), "viewed_quote", random_quote.get("quote", ""))
    return render_template("quotes.html", user=user, random_quote=random_quote)


@app.route("/images", methods=["GET", "POST"])
def images():
    user = get_current_user()
    image_filename = None
    if request.method == "POST" and request.form.get("action") == "random":
        images_list = list(db.images.find({}, {"_id": 0}))
        if images_list:
            choice = random.choice(images_list)
            candidate = os.path.join(IMAGES_FOLDER, choice.get("file", ""))
            if os.path.exists(candidate):
                image_filename = choice.get("file")
                if user:
                    log_activity(user.get("email"), "viewed_image", image_filename)
    return render_template("images.html", user=user, image_filename=image_filename)


@app.route("/music", methods=["GET", "POST"])
def music():
    user = get_current_user()
    song = None
    if request.method == "POST" and request.form.get("action") == "random":
        songs_list = list(db.songs.find({}, {"_id": 0}))
        if songs_list:
            choice = random.choice(songs_list)
            candidate = os.path.join(MUSIC_FOLDER, choice.get("file", ""))
            if os.path.exists(candidate):
                song = choice
                if user:
                    log_activity(user.get("email"), "played_song", f"{song.get('title','')} - {song.get('artist','')}")
    return render_template("music.html", user=user, song=song)


# --- GAMES ---
@app.route("/games")
def games():
    user = get_current_user()
    return render_template("games/index.html", user=user)

# --- ENHANCED GAME ROUTES ---
@app.route("/games/breathing", methods=["GET", "POST"])
def game_breathing():
    user = get_current_user()
    if not user:
        flash("Please login to play games.", "warning")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "complete_session":
            session_data = {
                "duration": int(request.form.get("duration", 0)),
                "cycles_completed": int(request.form.get("cycles", 0)),
                "focus_score": _calculate_focus_score({
                    "accuracy": 1.0,  # Breathing exercises are about completion
                    "avg_reaction_time": 0,
                    "consistency": float(request.form.get("consistency", 0.8))
                })
            }
            _log_game_session(user["email"], "breathing", session_data)
            _update_game_score(user["email"], "breathing", {
                "sessions_completed": 1,
                "total_duration": session_data["duration"],
                "total_cycles": session_data["cycles_completed"]
            })
            log_activity(user["email"], "breathing_completed", f"Completed {session_data['cycles_completed']} breathing cycles")
            flash("Great job! Your breathing session has been recorded.", "success")
    
    stats = _get_user_game_stats(user["email"], "breathing")
    return render_template("games/breathing.html", user=user, stats=stats)

@app.route("/games/memory", methods=["GET", "POST"])
def game_memory():
    user = get_current_user()
    if not user:
        flash("Please login to play games.", "warning")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "complete_game":
            session_data = {
                "moves": int(request.form.get("moves", 0)),
                "time_taken": int(request.form.get("time_taken", 0)),
                "pairs_found": int(request.form.get("pairs_found", 0)),
                "accuracy": float(request.form.get("accuracy", 0)),
                "focus_score": _calculate_focus_score({
                    "accuracy": float(request.form.get("accuracy", 0)),
                    "avg_reaction_time": int(request.form.get("avg_reaction_time", 1000)),
                    "consistency": float(request.form.get("consistency", 0.7))
                })
            }
            _log_game_session(user["email"], "memory", session_data)
            _update_game_score(user["email"], "memory", {
                "games_played": 1,
                "total_moves": session_data["moves"],
                "total_time": session_data["time_taken"],
                "pairs_found": session_data["pairs_found"]
            })
            log_activity(user["email"], "memory_completed", f"Memory game: {session_data['pairs_found']} pairs in {session_data['moves']} moves")
            flash("Excellent memory work! Your performance has been recorded.", "success")
    
    stats = _get_user_game_stats(user["email"], "memory")
    return render_template("games/memory.html", user=user, stats=stats)

@app.route("/games/reaction", methods=["GET", "POST"])
def game_reaction():
    user = get_current_user()
    if not user:
        flash("Please login to play games.", "warning")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "complete_test":
            session_data = {
                "avg_reaction_time": float(request.form.get("avg_reaction_time", 0)),
                "best_time": float(request.form.get("best_time", 0)),
                "worst_time": float(request.form.get("worst_time", 0)),
                "rounds": int(request.form.get("rounds", 0)),
                "focus_score": _calculate_focus_score({
                    "accuracy": 1.0,  # Reaction time games are about speed
                    "avg_reaction_time": float(request.form.get("avg_reaction_time", 0)),
                    "consistency": float(request.form.get("consistency", 0.8))
                })
            }
            _log_game_session(user["email"], "reaction", session_data)
            _update_game_score(user["email"], "reaction", {
                "tests_completed": 1,
                "total_rounds": session_data["rounds"],
                "best_time": session_data["best_time"]
            })
            log_activity(user["email"], "reaction_completed", f"Reaction test: {session_data['avg_reaction_time']:.0f}ms average")
            flash("Great reflexes! Your reaction time has been recorded.", "success")
    
    stats = _get_user_game_stats(user["email"], "reaction")
    return render_template("games/reaction.html", user=user, stats=stats)

@app.route("/games/puzzle", methods=["GET", "POST"])
def game_puzzle():
    user = get_current_user()
    if not user:
        flash("Please login to play games.", "warning")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "complete_puzzle":
            session_data = {
                "puzzle_type": request.form.get("puzzle_type", "sliding"),
                "moves": int(request.form.get("moves", 0)),
                "time_taken": int(request.form.get("time_taken", 0)),
                "hints_used": int(request.form.get("hints_used", 0)),
                "focus_score": _calculate_focus_score({
                    "accuracy": float(request.form.get("accuracy", 0.9)),
                    "avg_reaction_time": int(request.form.get("avg_reaction_time", 500)),
                    "consistency": float(request.form.get("consistency", 0.8))
                })
            }
            _log_game_session(user["email"], "puzzle", session_data)
            _update_game_score(user["email"], "puzzle", {
                "puzzles_completed": 1,
                "total_moves": session_data["moves"],
                "total_time": session_data["time_taken"]
            })
            log_activity(user["email"], "puzzle_completed", f"Puzzle solved: {session_data['puzzle_type']} in {session_data['moves']} moves")
            flash("Puzzle solved! Your problem-solving skills are improving.", "success")
    
    stats = _get_user_game_stats(user["email"], "puzzle")
    return render_template("games/puzzle.html", user=user, stats=stats)

@app.route("/games/leaderboard")
def game_leaderboard():
    user = get_current_user()
    
    # Get leaderboards for different games
    leaderboards = {}
    games = ["breathing", "memory", "reaction", "puzzle", "rps", "guess", "trivia"]
    
    for game in games:
        if game == "breathing":
            leaderboards[game] = list(db.game_scores.find({"game": game}).sort("total_cycles", -1).limit(10))
        elif game == "memory":
            leaderboards[game] = list(db.game_scores.find({"game": game}).sort("pairs_found", -1).limit(10))
        elif game == "reaction":
            leaderboards[game] = list(db.game_scores.find({"game": game}).sort("best_time", 1).limit(10))  # Lower is better
        elif game == "puzzle":
            leaderboards[game] = list(db.game_scores.find({"game": game}).sort("total_moves", 1).limit(10))  # Lower is better
        elif game == "rps":
            leaderboards[game] = list(db.game_scores.find({"game": game}).sort("wins", -1).limit(10))
        elif game == "guess":
            leaderboards[game] = list(db.game_scores.find({"game": game}).sort("wins", -1).limit(10))
        elif game == "trivia":
            leaderboards[game] = list(db.game_scores.find({"game": game}).sort("correct", -1).limit(10))
    
    return render_template("games/leaderboard.html", user=user, leaderboards=leaderboards)

# --- EXISTING GAME ROUTES WITH ENHANCED TRACKING ---
@app.route("/games/rps", methods=["GET", "POST"])
def game_rps():
    user = get_current_user()
    if not user:
        flash("Please login to play games.", "warning")
        return redirect(url_for("login"))
    
    player = None
    computer = None
    result = None
    
    if request.method == "POST":
        choice = request.form.get("choice")
        if choice:
            choices = ["rock", "paper", "scissors"]
            computer_choice = random.choice(choices)
            player = choice
            computer = computer_choice
            
            if player == computer:
                result = "It's a draw!"
                _update_game_score(user["email"], "rps", {"draws": 1})
                log_activity(user["email"], "rps_draw", f"Player: {player}, Computer: {computer}")
            elif (player == "rock" and computer == "scissors") or \
                 (player == "paper" and computer == "rock") or \
                 (player == "scissors" and computer == "paper"):
                result = "You win!"
                _update_game_score(user["email"], "rps", {"wins": 1})
                log_activity(user["email"], "rps_win", f"Player: {player}, Computer: {computer}")
            else:
                result = "You lose!"
                _update_game_score(user["email"], "rps", {"losses": 1})
                log_activity(user["email"], "rps_loss", f"Player: {player}, Computer: {computer}")
            
            _update_game_score(user["email"], "rps", {"games_played": 1})
    
    stats = _get_user_game_stats(user["email"], "rps")
    return render_template("games/rps.html", user=user, player=player, computer=computer, result=result, stats=stats)

@app.route("/games/guess", methods=["GET", "POST"])
def game_guess():
    user = get_current_user()
    if not user:
        flash("Please login to play games.", "warning")
        return redirect(url_for("login"))
    
    feedback = None
    won = False
    attempts = 0
    target = None
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "reset":
            session.pop("target_number", None)
            session.pop("attempts", None)
            return redirect(url_for("game_guess"))
        elif action == "guess":
            guess = int(request.form.get("guess", 0))
            target = session.get("target_number")
            attempts = session.get("attempts", 0)
            
            if not target:
                target = random.randint(1, 100)
                session["target_number"] = target
                attempts = 0
            
            attempts += 1
            session["attempts"] = attempts
            
            if guess < target:
                feedback = "Too low! Try again."
            elif guess > target:
                feedback = "Too high! Try again."
            else:
                feedback = f"Correct! You guessed it in {attempts} attempts."
                won = True
                _update_game_score(user["email"], "guess", {
                    "wins": 1,
                    "total_attempts": attempts
                }, {"best_attempts": attempts})
                log_activity(user["email"], "guess_won", f"Guessed {target} in {attempts} attempts")
                session.pop("target_number", None)
                session.pop("attempts", None)
    
    stats = _get_user_game_stats(user["email"], "guess")
    return render_template("games/guess_number.html", user=user, feedback=feedback, won=won, attempts=attempts, stats=stats)

@app.route("/games/trivia", methods=["GET", "POST"])
def game_trivia():
    user = get_current_user()
    if not user:
        flash("Please login to play games.", "warning")
        return redirect(url_for("login"))
    
    # Trivia questions
    questions = [
        {"q": "What is the capital of France?", "a": "paris"},
        {"q": "What is 2 + 2?", "a": "4"},
        {"q": "What is the largest planet in our solar system?", "a": "jupiter"},
        {"q": "Who painted the Mona Lisa?", "a": "leonardo da vinci"},
        {"q": "What is the smallest country in the world?", "a": "vatican"},
        {"q": "What is the chemical symbol for gold?", "a": "au"},
        {"q": "In what year did World War II end?", "a": "1945"},
        {"q": "What is the fastest land animal?", "a": "cheetah"},
        {"q": "What is the largest ocean on Earth?", "a": "pacific"},
        {"q": "Who wrote 'Romeo and Juliet'?", "a": "shakespeare"}
    ]
    
    question = random.choice(questions)
    feedback = None
    
    if request.method == "POST":
        answer = request.form.get("answer", "").strip().lower()
        if answer == question["a"]:
            feedback = "Correct! Well done!"
            _update_game_score(user["email"], "trivia", {"correct": 1})
            log_activity(user["email"], "trivia_correct", f"Question: {question['q']}")
        else:
            feedback = f"Incorrect! The correct answer was: {question['a']}"
            _update_game_score(user["email"], "trivia", {"incorrect": 1})
            log_activity(user["email"], "trivia_incorrect", f"Question: {question['q']}")
        
        _update_game_score(user["email"], "trivia", {"games_played": 1})
        question = random.choice(questions)  # New question for next round
    
    stats = _get_user_game_stats(user["email"], "trivia")
    return render_template("games/trivia.html", user=user, question=question, feedback=feedback, stats=stats)

# --- NOTIFICATION ROUTES ---
@app.route("/notifications")
def notifications():
    if not require_login():
        return redirect(url_for("login"))
    
    user = get_current_user()
    user_notifications = get_user_notifications(user["email"])
    
    return render_template("notifications.html", user=user, notifications=user_notifications)

@app.route("/api/notifications/check")
def check_user_notifications():
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    user = get_current_user()
    new_achievements = check_achievements(user["email"])
    
    # Save new notifications
    for notification in new_achievements:
        save_notification(user["email"], notification)
    
    return jsonify({
        "notifications": new_achievements,
        "motivational_message": get_motivational_message(user["email"]),
        "insights": get_progress_insights(user["email"])
    })

@app.route("/api/notifications/mark-read", methods=["POST"])
def mark_notification_read():
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    data = request.get_json()
    notification_id = data.get("notification_id")
    
    if notification_id:
        from bson import ObjectId
        db.notifications.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"read": True}}
        )
    
    return jsonify({"success": True})

@app.route("/api/progress/summary")
def get_progress_summary():
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    user = get_current_user()
    summary = get_weekly_progress_summary(user["email"])
    
    return jsonify(summary)

# --- MOOD ASSESSMENT ROUTES ---
@app.route("/mood-assessment")
def mood_assessment():
    if not require_login():
        return redirect(url_for("login"))
    
    try:
        user = get_current_user()
        # Get 5 random questions for quick assessment
        quick_questions = mood_assessor.get_random_questions(5)
        
        return render_template("mood_assessment.html", user=user, questions=HEALTH_QUESTIONS, quick_questions=quick_questions)
    except Exception as e:
        print(f"Error in mood assessment route: {e}")
        import traceback
        traceback.print_exc()
        flash(f"Error loading mood assessment: {str(e)}", "error")
        return redirect(url_for("home"))

@app.route("/api/mood-assessment", methods=["POST"])
def api_mood_assessment():
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
            
        responses = data.get("responses", [])
        is_quick = data.get("is_quick", False)
        game_data = data.get("game_data", None)
        
        print(f"Received mood assessment data: {type(responses)} with {len(responses) if isinstance(responses, (list, dict)) else 'unknown'} items")
        print(f"Responses: {responses}")
        
        if not responses:
            return jsonify({"error": "No responses provided"}), 400
        
        if game_data:
            print(f"Game data included: {list(game_data.keys())}")
        
        # Get enhanced analysis with game data
        analysis = mood_assessor.get_mood_analysis(responses, game_data)
        print(f"Analysis generated: {analysis['mood_category']}")
        
        # Log detected conditions
        if analysis.get('detected_conditions'):
            print(f"Detected conditions: {list(analysis['detected_conditions'].keys())}")
        
        # Save assessment with game data
        assessment_data = {
            "user_email": user["email"],
            "responses": responses,
            "analysis": analysis,
            "game_data": game_data,
            "timestamp": datetime.utcnow()
        }
        db.mood_assessments.insert_one(assessment_data)
        print("Assessment saved to database")
        
        # Log activity
        activity_msg = f"Score: {analysis['overall_score']}, Category: {analysis['mood_category']}"
        if analysis.get('detected_conditions'):
            conditions = list(analysis['detected_conditions'].keys())
            activity_msg += f", Conditions: {', '.join(conditions)}"
        log_activity(user["email"], "mood_assessment_completed", activity_msg)
        
        return jsonify({
            "success": True,
            "analysis": analysis
        })
    
    except Exception as e:
        print(f"Error in mood assessment API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route("/api/debug-mood", methods=["POST"])
def debug_mood_assessment():
    """Debug endpoint for mood assessment"""
    try:
        data = request.get_json()
        responses = data.get("responses", {})
        
        # Test the mood assessor directly
        analysis = mood_assessor.get_mood_analysis(responses)
        
        return jsonify({
            "success": True,
            "debug_info": {
                "responses_type": type(responses).__name__,
                "responses_count": len(responses) if isinstance(responses, (list, dict)) else 0,
                "analysis_keys": list(analysis.keys()) if isinstance(analysis, dict) else [],
                "mood_category": analysis.get('mood_category', 'Unknown'),
                "overall_score": analysis.get('overall_score', 'Unknown')
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route("/api/game-performance", methods=["POST"])
def api_game_performance():
    """Track game performance for mood analysis integration"""
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    try:
        user = get_current_user()
        data = request.get_json()
        game_type = data.get("game_type")
        performance_data = data.get("performance_data", {})
        
        if not game_type:
            return jsonify({"error": "Game type required"}), 400
        
        # Log game performance
        _log_game_session(user["email"], game_type, performance_data)
        
        # Update game scores
        if "score" in performance_data:
            _update_game_score(user["email"], game_type, {"score": performance_data["score"]})
        
        # Log activity
        log_activity(user["email"], f"game_{game_type}_played", f"Performance: {performance_data}")
        
        return jsonify({"success": True, "message": "Game performance tracked"})
    
    except Exception as e:
        print(f"Error tracking game performance: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/mental-health-guidance", methods=["POST"])
def api_mental_health_guidance():
    """Get personalized mental health guidance based on assessment and game performance"""
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    try:
        user = get_current_user()
        data = request.get_json()
        condition = data.get("condition")
        
        if not condition:
            return jsonify({"error": "Mental health condition required"}), 400
        
        # Get guidance based on condition
        guidance = {
            "depression": {
                "immediate_actions": [
                    "Reach out to a trusted friend or family member",
                    "Practice deep breathing exercises",
                    "Go for a short walk outside",
                    "Listen to uplifting music"
                ],
                "long_term_strategies": [
                    "Consider professional therapy or counseling",
                    "Establish a regular sleep schedule",
                    "Engage in regular physical exercise",
                    "Practice mindfulness and meditation"
                ],
                "warning_signs": [
                    "Persistent sadness or hopelessness",
                    "Loss of interest in activities",
                    "Changes in sleep or appetite",
                    "Thoughts of self-harm"
                ],
                "resources": [
                    "National Suicide Prevention Lifeline: 988",
                    "Crisis Text Line: Text HOME to 741741",
                    "Find a therapist: psychologytoday.com"
                ]
            },
            "anxiety": {
                "immediate_actions": [
                    "Practice 4-7-8 breathing technique",
                    "Use grounding techniques (5-4-3-2-1 method)",
                    "Take a break from stressful situations",
                    "Practice progressive muscle relaxation"
                ],
                "long_term_strategies": [
                    "Consider cognitive behavioral therapy (CBT)",
                    "Limit caffeine and alcohol intake",
                    "Establish a regular routine",
                    "Practice mindfulness meditation"
                ],
                "warning_signs": [
                    "Excessive worry or fear",
                    "Restlessness or feeling on edge",
                    "Panic attacks",
                    "Avoidance of certain situations"
                ],
                "resources": [
                    "Anxiety and Depression Association of America",
                    "Find a therapist: goodtherapy.org",
                    "Mindfulness apps: Headspace, Calm"
                ]
            }
        }
        
        condition_guidance = guidance.get(condition, {
            "immediate_actions": ["Seek professional help", "Practice self-care"],
            "long_term_strategies": ["Consider therapy", "Build support network"],
            "warning_signs": ["Monitor symptoms", "Seek help if worsening"],
            "resources": ["Contact mental health professional"]
        })
        
        return jsonify({
            "success": True,
            "guidance": condition_guidance,
            "condition": condition
        })
    
    except Exception as e:
        print(f"Error getting mental health guidance: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/mood-history")
def mood_history():
    if not require_login():
        return redirect(url_for("login"))
    
    user = get_current_user()
    assessments = mood_assessor.get_user_mood_history(user["email"], 30)
    
    return render_template("mood_history.html", user=user, assessments=assessments)

@app.route("/mental-health-guidance")
def mental_health_guidance():
    if not require_login():
        return redirect(url_for("login"))
    
    user = get_current_user()
    return render_template("mental_health_guidance.html", user=user)

@app.route("/wellness-center")
def wellness_center():
    if not require_login():
        return redirect(url_for("login"))
    
    user = get_current_user()
    return render_template("wellness_center.html", user=user)

@app.route("/fitness-tracker")
def fitness_tracker():
    if not require_login():
        return redirect(url_for("login"))
    
    user = get_current_user()
    return render_template("fitness_tracker.html", user=user)

@app.route("/daily-challenges")
def daily_challenges():
    if not require_login():
        return redirect(url_for("login"))
    
    user = get_current_user()
    return render_template("daily_challenges.html", user=user)

@app.route("/api/user-assessment-history")
def api_user_assessment_history():
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    try:
        user = get_current_user()
        assessments = mood_assessor.get_user_mood_history(user["email"], 7)  # Last 7 days
        
        return jsonify({
            "success": True,
            "assessments": assessments
        })
    
    except Exception as e:
        print(f"Error getting assessment history: {e}")
        return jsonify({"error": str(e)}), 500

# --- CHATBOT ROUTES ---
@app.route("/chatbot")
def chatbot():
    if not require_login():
        return redirect(url_for("login"))
    
    user = get_current_user()
    return render_template("chatbot.html", user=user)

@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    # Allow anonymous users for testing
    user = None
    user_email = None
    user_mood = "moderate"
    
    if require_login():
        user = get_current_user()
        user_email = user["email"]
        user_mood = user.get("current_mood", "moderate")
    else:
        # Anonymous user - use session ID as identifier
        user_email = f"anonymous_{session.get('session_id', 'unknown')}"
    
    data = request.get_json()
    message = data.get("message", "").strip()
    conversation_id = data.get("conversation_id")
    
    if not message:
        return jsonify({
            "success": False,
            "error": "Message cannot be empty"
        })
    
    try:
        # Generate response
        response_data = health_chatbot.generate_response(
            message, 
            user_email, 
            conversation_id
        )
        
        # Get quick responses based on user's mood
        quick_responses = health_chatbot.get_quick_responses(user_mood)
        
        return jsonify({
            "success": True,
            "response": response_data["response"],
            "quick_responses": quick_responses[:5],  # Limit to 5 quick responses
            "timestamp": response_data["timestamp"].isoformat()
        })
        
    except Exception as e:
        print(f"Error in chatbot: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "Chatbot service unavailable"
        })

@app.route("/api/chatbot/insights")
def api_chatbot_insights():
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    user = get_current_user()
    
    try:
        insights = health_chatbot.generate_health_insights(user["email"])
        return jsonify({
            "success": True,
            "insights": insights
        })
        
    except Exception as e:
        print(f"Error generating insights: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to generate insights"
        })

@app.route("/api/chatbot/resources")
def api_chatbot_resources():
    topic = request.args.get("topic", "general")
    
    try:
        resources = health_chatbot.get_mental_health_resources(topic)
        return jsonify({
            "success": True,
            "resources": resources
        })
        
    except Exception as e:
        print(f"Error getting resources: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to fetch resources"
        })

# --- ENHANCED HEALTH & WELLNESS API ENDPOINTS ---

@app.route("/api/health-tips")
def api_health_tips():
    """Get daily health and wellness tips"""
    category = request.args.get("category", "general")
    
    try:
        tips = health_chatbot.get_daily_health_tips(category)
        return jsonify({
            "success": True,
            "tips": tips,
            "category": category
        })
    except Exception as e:
        print(f"Error getting health tips: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to fetch health tips"
        })

@app.route("/api/fitness-suggestions")
def api_fitness_suggestions():
    """Get personalized fitness suggestions"""
    fitness_level = request.args.get("level", "beginner")
    
    try:
        suggestions = health_chatbot.get_fitness_suggestions(fitness_level)
        return jsonify({
            "success": True,
            "suggestions": suggestions,
            "level": fitness_level
        })
    except Exception as e:
        print(f"Error getting fitness suggestions: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to fetch fitness suggestions"
        })

@app.route("/api/sleep-tips")
def api_sleep_tips():
    """Get sleep improvement tips"""
    try:
        tips = health_chatbot.get_sleep_improvement_tips()
        return jsonify({
            "success": True,
            "tips": tips
        })
    except Exception as e:
        print(f"Error getting sleep tips: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to fetch sleep tips"
        })

@app.route("/api/nutrition-guidance")
def api_nutrition_guidance():
    """Get nutrition guidance based on goals"""
    goal = request.args.get("goal", "general_health")
    
    try:
        guidance = health_chatbot.get_nutrition_guidance(goal)
        return jsonify({
            "success": True,
            "guidance": guidance,
            "goal": goal
        })
    except Exception as e:
        print(f"Error getting nutrition guidance: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to fetch nutrition guidance"
        })

@app.route("/api/mood-activities")
def api_mood_activities():
    """Get mood-based activity suggestions"""
    mood = request.args.get("mood", "moderate")
    
    try:
        activities = health_chatbot.get_mood_based_activities(mood)
        return jsonify({
            "success": True,
            "activities": activities,
            "mood": mood
        })
    except Exception as e:
        print(f"Error getting mood activities: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to fetch mood activities"
        })

@app.route("/api/symptom-guidance", methods=["POST"])
def api_symptom_guidance():
    """Get general health guidance for symptoms (not diagnosis)"""
    if not require_login():
        return jsonify({"error": "Not logged in"})
    
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", "")
        
        if not symptoms:
            return jsonify({
                "success": False,
                "error": "Symptoms required"
            })
        
        guidance = health_chatbot.get_symptom_guidance(symptoms)
        
        return jsonify({
            "success": True,
            "guidance": guidance,
            "symptoms": symptoms,
            "disclaimer": "This is general health guidance only. Always consult a healthcare provider for medical concerns."
        })
        
    except Exception as e:
        print(f"Error getting symptom guidance: {e}")
        return jsonify({
            "success": False,
            "error": "Unable to process symptom guidance"
        })


@app.route("/upload", methods=["GET", "POST"])
def upload():
    print(f"🔍 Upload route accessed. Session: {session.get('user_email')}")  # Debug
    
    if not require_login():
        print("❌ Login required - redirecting to login")  # Debug
        return redirect(url_for("login"))
    
    user = get_current_user()
    print(f"✅ User authenticated: {user}")  # Debug

    if request.method == "POST":
        try:
            # Quote upload
            if request.form.get("form_name") == "quote":
                quote_text = request.form.get("quote", "").strip()
                author = request.form.get("author", "").strip() or "Unknown"
                if quote_text:
                    db.quotes.insert_one({"quote": quote_text, "author": author})
                    flash("Quote saved!", "success")
                else:
                    flash("Please enter a quote.", "warning")

            # Image upload
            if request.form.get("form_name") == "image" and "image_file" in request.files:
                f = request.files["image_file"]
                if f and f.filename:
                    os.makedirs(IMAGES_FOLDER, exist_ok=True)
                    save_path = os.path.join(IMAGES_FOLDER, f.filename)
                    f.save(save_path)
                    db.images.insert_one({"file": f.filename})
                    flash("Image uploaded!", "success")
                else:
                    flash("Please select an image file.", "warning")

            # Song upload
            if request.form.get("form_name") == "song" and "song_file" in request.files:
                title = request.form.get("title", "").strip()
                artist = request.form.get("artist", "").strip() or "Unknown"
                f = request.files["song_file"]
                if title and f and f.filename:
                    os.makedirs(MUSIC_FOLDER, exist_ok=True)
                    save_path = os.path.join(MUSIC_FOLDER, f.filename)
                    f.save(save_path)
                    db.songs.insert_one({"title": title, "artist": artist, "file": f.filename})
                    flash("Song uploaded!", "success")
                else:
                    flash("Please enter song title and select a file.", "warning")
        except Exception as e:
            flash(f"Upload error: {str(e)}", "danger")
            print(f"Upload error: {e}")

    return render_template("upload.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        print(f"Login attempt: {email}")  # Debug
        
        try:
            # Test database connection
            db.users.find_one()
            user = db.users.find_one({"email": email, "password": password}, {"_id": 0})
            
            if user:
                session["user_email"] = user["email"]
                # Respect remember-me checkbox
                session.permanent = bool(request.form.get("remember"))
                flash(f"Welcome back, {user.get('first_name', 'User')}!", "success")
                log_activity(user.get('email'), 'login', 'user logged in')
                print(f"✅ User logged in successfully: {user['email']}")  # Debug
                print(f"✅ Session set: {session.get('user_email')}")  # Debug
                return redirect(url_for("home"))
            else:
                # Check if user exists but wrong password
                existing_user = db.users.find_one({"email": email}, {"_id": 0})
                if existing_user:
                    flash("❌ Invalid password. Please try again.", "danger")
                    print(f"❌ Wrong password for: {email}")  # Debug
                else:
                    flash("❌ No account found with this email. Please register first.", "warning")
                    print(f"❌ No user found: {email}")  # Debug
        except Exception as e:
            flash(f"❌ Database connection error: {str(e)}", "danger")
            print(f"❌ Login error: {e}")
    
    return render_template("login.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            flash("Please enter your email.", "warning")
        else:
            # Create password reset token if user exists
            user = db.users.find_one({"email": email})
            if user:
                token = secrets.token_urlsafe(32)
                expires_at = datetime.utcnow() + timedelta(hours=1)
                db.password_resets.insert_one({
                    "email": email,
                    "token": token,
                    "expires_at": expires_at,
                    "used": False,
                    "created_at": datetime.utcnow(),
                })
                reset_url = url_for("reset_password", token=token, _external=True)
                # Simulate sending email by printing the link to server logs
                print(f"[PASSWORD RESET] Send this link to {email}: {reset_url}")
                log_activity(email, "forgot_password", "requested reset link")
                return render_template("reset_sent.html", email=email, reset_url=reset_url)
            else:
                flash("If this email exists, a reset link has been sent.", "info")
                return redirect(url_for("login"))
    return render_template("forgot.html", user=get_current_user())


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    rec = db.password_resets.find_one({"token": token})
    if not rec:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("forgot"))
    if rec.get("used"):
        flash("This reset link has already been used.", "warning")
        return redirect(url_for("login"))
    if rec.get("expires_at") and datetime.utcnow() > rec["expires_at"]:
        flash("This reset link has expired.", "danger")
        return redirect(url_for("forgot"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not password:
            flash("Please enter a new password.", "warning")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "warning")
        else:
            email = rec.get("email")
            db.users.update_one({"email": email}, {"$set": {"password": password}})
            db.password_resets.update_one({"_id": rec["_id"]}, {"$set": {"used": True, "used_at": datetime.utcnow()}})
            flash("Your password has been reset. Please login.", "success")
            return redirect(url_for("login"))

    return render_template("reset.html", token=token)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        print(f"Registration attempt: {email}")  # Debug

        if not (first_name and last_name and email and password):
            flash("❌ All fields are required.", "danger")
        elif password != confirm:
            flash("❌ Passwords do not match.", "danger")
        elif len(password) < 6:
            flash("❌ Password must be at least 6 characters.", "danger")
        elif not email or "@" not in email:
            flash("❌ Please enter a valid email address.", "danger")
        else:
            try:
                # Test database connection
                db.users.find_one()
                
                # Check if user already exists
                existing_user = db.users.find_one({"email": email})
                if existing_user:
                    flash("⚠️ An account with this email already exists.", "warning")
                    print(f"❌ User already exists: {email}")  # Debug
                else:
                    # Create new user
                    db.users.insert_one({
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "password": password,
                    })
                    flash("✅ Account created successfully! Please login.", "success")
                    print(f"✅ User registered: {email}")  # Debug
                    return redirect(url_for("login"))
            except Exception as e:
                flash(f"❌ Database error: {str(e)}", "danger")
                print(f"❌ Registration error: {e}")

    return render_template("register.html")


@app.route("/logout")
def logout():
    email = session.get("user_email")
    if email:
        log_activity(email, "logout", "user logged out")
    session.pop("user_email", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# --- ACTIVITY & REPORTS ---
def _aggregate_activity(email: str, start: datetime, end: datetime):
    pipeline = [
        {"$match": {"user_email": email, "timestamp": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return list(db.user_activity.aggregate(pipeline))


@app.route("/activity")
def activity():
    if not require_login():
        return redirect(url_for("login"))
    user = get_current_user()
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    weekly = _aggregate_activity(user["email"], week_start, now)
    monthly = _aggregate_activity(user["email"], month_start, now)
    recent = list(db.user_activity.find({"user_email": user["email"]}).sort("timestamp", -1).limit(50))
    return render_template("activity.html", user=user, weekly=weekly, monthly=monthly, recent=recent)


def _csv(iter_rows, headers):
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in iter_rows:
        writer.writerow(row)
    buf.seek(0)
    return buf.getvalue()


@app.route("/activity/download/weekly.csv")
def download_weekly():
    if not require_login():
        return redirect(url_for("login"))
    user = get_current_user()
    now = datetime.utcnow()
    start = now - timedelta(days=7)
    rows = db.user_activity.find({"user_email": user["email"], "timestamp": {"$gte": start, "$lt": now}}).sort("timestamp", -1)
    csv_data = _csv(((r.get("timestamp"), r.get("action"), r.get("details")) for r in rows), ["timestamp", "action", "details"])
    return send_file(
        io.BytesIO(csv_data.encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="activity_weekly.csv",
    )


@app.route("/activity/download/monthly.csv")
def download_monthly():
    if not require_login():
        return redirect(url_for("login"))
    user = get_current_user()
    now = datetime.utcnow()
    start = now - timedelta(days=30)
    rows = db.user_activity.find({"user_email": user["email"], "timestamp": {"$gte": start, "$lt": now}}).sort("timestamp", -1)
    csv_data = _csv(((r.get("timestamp"), r.get("action"), r.get("details")) for r in rows), ["timestamp", "action", "details"])
    return send_file(
        io.BytesIO(csv_data.encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="activity_monthly.csv",
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect(url_for("login"))
    user = get_current_user()
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if not (current and new and confirm):
            flash("All fields are required.", "warning")
        elif new != confirm:
            flash("New passwords do not match.", "danger")
        elif len(new) < 6:
            flash("New password must be at least 6 characters.", "warning")
        else:
            # verify current
            doc = db.users.find_one({"email": user.get("email")})
            if not doc or doc.get("password") != current:
                flash("Current password is incorrect.", "danger")
            else:
                result = db.users.update_one({"email": user.get("email")}, {"$set": {"password": new}})
                if result.modified_count:
                    flash("Password updated successfully.", "success")
                else:
                    flash("No changes made.", "info")
                log_activity(user["email"], "changed_password", "profile page")
                return redirect(url_for("profile"))
    return render_template("profile.html", user=user)


@app.route("/test-session")
def test_session():
    """Test session and user authentication"""
    email = session.get("user_email")
    user = get_current_user()
    
    return f"""
    <h2>Session Test</h2>
    <p><strong>Session Email:</strong> {email}</p>
    <p><strong>Current User:</strong> {user}</p>
    <p><strong>Login Required Test:</strong> {require_login()}</p>
    <p><a href="/login">Login</a> | <a href="/upload">Upload</a></p>
    """


@app.route("/test-db")
def test_db():
    """Test database connection and create test user if needed"""
    try:
        # Test connection
        db.users.find_one()
        
        # Check collections
        collections = db.list_collection_names()
        
        # Check if test user exists
        test_user = db.users.find_one({"email": "test@example.com"})
        if not test_user:
            # Create test user
            db.users.insert_one({
                "first_name": "Test",
                "last_name": "User", 
                "email": "test@example.com",
                "password": "password123"
            })
            return f"""
            <h2>✅ Database Connected Successfully!</h2>
            <p><strong>Collections:</strong> {', '.join(collections)}</p>
            <p><strong>Test User Created:</strong> test@example.com / password123</p>
            <p><a href="/login">Go to Login</a></p>
            """
        else:
            return f"""
            <h2>✅ Database Connected Successfully!</h2>
            <p><strong>Collections:</strong> {', '.join(collections)}</p>
            <p><strong>Test User Exists:</strong> test@example.com / password123</p>
            <p><a href="/login">Go to Login</a></p>
            """
    except Exception as e:
        return f"""
        <h2>❌ Database Connection Failed!</h2>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Solution:</strong> Make sure MongoDB is running on localhost:27017</p>
        <p>Start MongoDB with: <code>mongod</code></p>
        """


# --- MEDIA SERVING ---
@app.route("/media/image/<path:filename>")
def media_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)


@app.route("/media/music/<path:filename>")
def media_music(filename):
    return send_from_directory(MUSIC_FOLDER, filename)


@app.route("/media/bg")
def bg_image():
    # Serve the background image from an absolute path if it exists
    try:
        if BG_IMAGE_PATH and os.path.exists(BG_IMAGE_PATH):
            return send_file(BG_IMAGE_PATH)
    except Exception:
        pass
    # Fallback: use a static placeholder if provided
    fallback = os.path.join(app.static_folder or "static", "img", "meditate.jpg")
    if os.path.exists(fallback):
        return send_file(fallback)
    # Last resort: 404
    from flask import abort
    return abort(404)


# --- SIMPLE PUBLIC JSON APIS ---
@app.get("/api/random-quotes")
def api_random_quotes():
    try:
        limit = max(1, min(int(request.args.get("limit", 10)), 50))
    except ValueError:
        limit = 10
    try:
        # Prefer server-side sampling for performance
        pipeline = [{"$sample": {"size": limit}}, {"$project": {"_id": 0}}]
        docs = list(db.quotes.aggregate(pipeline))
        return jsonify({"items": docs})
    except Exception:
        docs = list(db.quotes.find({}, {"_id": 0}))
        random.shuffle(docs)
        return jsonify({"items": docs[:limit]})


@app.get("/api/random-images")
def api_random_images():
    try:
        limit = max(1, min(int(request.args.get("limit", 12)), 60))
    except ValueError:
        limit = 12
    try:
        pipeline = [{"$sample": {"size": limit}}, {"$project": {"_id": 0}}]
        docs = list(db.images.aggregate(pipeline))
    except Exception:
        docs = list(db.images.find({}, {"_id": 0}))
        random.shuffle(docs)
        docs = docs[:limit]
    # Fallback to filesystem when DB is empty
    if not docs:
        try:
            files = [f for f in os.listdir(IMAGES_FOLDER) if os.path.isfile(os.path.join(IMAGES_FOLDER, f))]
            random.shuffle(files)
            files = files[:limit]
            docs = [{"file": f} for f in files]
        except Exception:
            docs = []
    # Add absolute media URLs
    for d in docs:
        file_name = d.get("file", "")
        d["url"] = url_for("media_image", filename=file_name)
    return jsonify({"items": docs})


@app.get("/api/random-songs")
def api_random_songs():
    try:
        limit = max(1, min(int(request.args.get("limit", 10)), 50))
    except ValueError:
        limit = 10
    try:
        pipeline = [{"$sample": {"size": limit}}, {"$project": {"_id": 0}}]
        docs = list(db.songs.aggregate(pipeline))
    except Exception:
        docs = list(db.songs.find({}, {"_id": 0}))
        random.shuffle(docs)
        docs = docs[:limit]
    # Enrich with media and download URLs
    for d in docs:
        file_name = d.get("file", "")
        d["url"] = url_for("media_music", filename=file_name)
        d["download_url"] = url_for("media_music", filename=file_name)
    return jsonify({"items": docs})


# --- SIMPLE MENTAL HEALTH CHATBOT API ---
@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    lower = message.lower()

    def reply(text: str, resources: list[dict] | None = None):
        return jsonify({
            "reply": text,
            "disclaimer": SUPPORT_DISCLAIMER,
            "resources": resources or []
        })

    if not message:
        return reply("Hi! I’m here to listen. How are you feeling today?")

    crisis_terms = ["suicide", "kill myself", "end my life", "harm myself", "self-harm"]
    if any(t in lower for t in crisis_terms):
        return reply(
            "I’m really sorry you’re going through this. Your life is important. "
            "Please contact emergency services or a suicide prevention line now (e.g., 988 in the U.S.). "
            "If you can, reach out to someone you trust nearby."
        )

    # Simple intent-based responses
    if any(k in lower for k in ["anxious", "anxiety", "panic"]):
        return reply(
            "Anxiety can be intense, but it’s manageable. Try box breathing: inhale 4s, hold 4s, exhale 6–8s for 2–3 minutes. "
            "Notice five things you can see, four you can touch, three you can hear, two you can smell, one you can taste.",
            resources=[
                {"label": "Breathing game", "url": url_for("games")},
                {"label": "Calming music", "url": url_for("music")},
            ]
        )
    if any(k in lower for k in ["depress", "sad", "down", "hopeless", "low mood"]):
        return reply(
            "I’m sorry you’re feeling low. Choose one small, kind action for yourself today (a short walk, shower, or text a friend). "
            "Writing down one thing you value about yourself can also help.",
            resources=[
                {"label": "Motivational quotes", "url": url_for("quotes")},
                {"label": "Happy images", "url": url_for("images")},
            ]
        )
    if any(k in lower for k in ["stress", "burnout", "overwhelmed", "pressure"]):
        return reply(
            "Let’s reduce the load: list tasks, pick the top one, set a 10–15 minute timer, and focus only on that. "
            "Relax your shoulders and jaw right now, then take five deep breaths.",
            resources=[
                {"label": "Focus music", "url": url_for("music")},
            ]
        )
    if any(k in lower for k in ["sleep", "insomnia", "can’t sleep", "cant sleep"]):
        return reply(
            "Help your body wind down: dim lights an hour before bed, avoid screens, and try a slow body scan from toes to head. "
            "If awake >20 minutes, get up, read something light, and try again.",
            resources=[
                {"label": "Sleepy playlist", "url": url_for("music")},
            ]
        )
    if any(k in lower for k in ["anger", "angry", "irritated", "frustrated"]):
        return reply(
            "Anger is a signal. Try the STOP skill: Stop, Take a breath, Observe sensations and thoughts, Proceed with intention. "
            "A brief walk or cold water on the wrists can also help reset.")
    if any(k in lower for k in ["lonely", "alone", "isolate"]):
        return reply(
            "Feeling lonely is hard. Consider messaging a trusted person or joining a community you care about. "
            "Even brief, positive interactions can lift mood.")
    if any(k in lower for k in ["focus", "concentrat", "productiv"]) :
        return reply(
            "Try the 25/5 focus cycle: 25 minutes on, 5 minutes off. Remove one distraction, and define a clear ‘done’ for this session.",
            resources=[{"label": "Play background music", "url": url_for("music")}] )

    # Default empathetic reflection
    return reply(
        "Thanks for sharing. I can offer coping techniques, supportive tips, and content to help you reset. "
        "Tell me more about what you’d like support with (sleep, stress, anxiety, mood, focus).",
        resources=[
            {"label": "Quotes", "url": url_for("quotes")},
            {"label": "Music", "url": url_for("music")},
            {"label": "Images", "url": url_for("images")},
        ]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # On Windows, the reloader and multi-threading can cause non-MainThread execution.
    # Disable both for stability.
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True, threaded=True)