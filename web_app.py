from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, send_file, flash, jsonify
from pymongo import MongoClient
import os
import random
import secrets
from datetime import datetime, timedelta
import re
from src.recommender import build_advanced_suggestions
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

    theme = {
        "brand": "#6f42c1",
        "brand2": "#20c997",
        "brand3": "#ff6b6b",
        "brand4": "#feca57",
    }

    return render_template("home.html", user=user, suggestions=suggestions, theme=theme)



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
    import csv, io
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
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True, threaded=True);
def register_user(first_name, last_name, email, password):
    """Register a new user. Returns (success, message)."""
    if db.users.find_one({"email": email}):
        return False, "Email already registered."
    db.users.insert_one({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    })
    return True, "Registration successful!"
def login_user(email, password):
    """Login a user. Returns (success, message)."""
    user = db.users.find_one({"email": email, "password": password})
    if user:
        return True, "Login successful!"
    return False, "Invalid email or password."
def load_quotes():
    return list(db.quotes.find({}, {"_id": 0}))
def save_quote(quote, author):
    db.quotes.insert_one({"quote": quote, "author": author})
def load_images():
    return list(db.images.find({}, {"_id": 0}))
def save_image(file_name):
    db.images.insert_one({"file": file_name})
def get_random_image():
    images = load_images()
    if images:
        img = random.choice(images)
        img_path = os.path.join(IMAGES_FOLDER, img["file"])
        if os.path.exists(img_path):
            return Image.open(img_path)
    return None
def load_songs():
    return list(db.songs.find({}, {"_id": 0}))
def save_song(title, artist, file_name):
    db.songs.insert_one({"title": title, "artist": artist, "file": file_name})
# --- STREAMLIT APP ---
st.set_page_config(page_title="Mood Minder", page_icon="😊", layout="centered")
# --- AUTHENTICATION ---
st.sidebar.title("User Account")
auth_option = st.sidebar.radio("Login / Register", ["Login", "Register"], key="auth_option")
current_user = None
if auth_option == "Register":
    st.sidebar.subheader("Create a new account")
    first_name = st.sidebar.text_input("First Name")
    last_name = st.sidebar.text_input("Last Name")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")
    if st.sidebar.button("Register"):
        if password == confirm_password:
            success, message = register_user(first_name, last_name, email, password)
            st.sidebar.success(message) if success else st.sidebar.error(message)
        else:
            st.sidebar.error("Passwords do not match.")
elif auth_option == "Login":
    st.sidebar.subheader("Login to your account")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        success, message = login_user(email, password)
        if success:
            current_user = db.users.find_one({"email": email}, {"_id": 0, "password": 0})
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)
if current_user:
    st.sidebar.markdown(f"**Logged in as:** {current_user.get('first_name', '')} {current_user.get('last_name', '')}")
    if st.sidebar.button("Logout"):
        current_user = None
        st.sidebar.info("You have been logged out.")
# --- CONTENT HELPERS ---   
def display_quote(quote):
    st.markdown(f"**{quote['quote']}**")
    st.markdown(f"*{quote['author']}*")
def display_image(image):
    st.image(image, use_column_width=True)
def display_song(song):
    st.markdown(f"**{song['title']}** by *{song['artist']}*")
    audio_path = os.path.join(MUSIC_FOLDER, song['file'])
    if os.path.exists(audio_path):
        audio_file = open(audio_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
# --- MAIN APP ---
st.title("😊 Mood Minder")
st.markdown("Your personal space for happiness and relaxation.")
if current_user:
    st.success(f"Welcome back, {current_user.get('first_name', '')}!")
    tab = st.selectbox("Choose an activity", ["Quotes", "Images", "Music", "Games", "Upload"])
    if tab == "Quotes":
        st.header("Daily Quotes")
        if st.button("Show Random Quote"):
            quotes = load_quotes()
            if quotes:
                quote = random.choice(quotes)
                display_quote(quote)
            else:
                st.info("No quotes available. Please upload some!")
    elif tab == "Images":
        st.header("Happy Images")
        if st.button("Show Random Image"):
            image = get_random_image()
            if image:
                display_image(image)
            else:
                st.info("No images available. Please upload some!")
    elif tab == "Music":
        st.header("Relaxing Music")
        if st.button("Play Random Song"):
            songs = load_songs()
            if songs:
                song = random.choice(songs)
                display_song(song)
            else:
                st.info("No songs available. Please upload some!")
    elif tab == "Games":
        st.header("Mini Games")
        game_choice = st.selectbox("Select a game", ["Rock-Paper-Scissors", "Guess the Number", "Trivia"])
        if game_choice == "Rock-Paper-Scissors":
            st.subheader("Rock-Paper-Scissors")
            user_choice = st.radio("Your choice:", ["rock", "paper", "scissors"])
            if st.button("Play"):
                computer_choice = random.choice(["rock", "paper", "scissors"])
                st.write(f"Computer chose: {computer_choice}")
                if user_choice == computer_choice:
                    st.info("It's a draw!")
                elif (user_choice == "rock" and computer_choice == "scissors") or \
                     (user_choice == "paper" and computer_choice == "rock") or \
                     (user_choice == "scissors" and computer_choice == "paper"):    
                    st.success("You win!")
                else:
                    st.error("You lose!")       
        elif game_choice == "Guess the Number":
            st.subheader("Guess the Number")
            if 'target_number' not in st.session_state:
                st.session_state.target_number = random.randint(1, 100)
                st.session_state.attempts = 0
            guess = st.number_input("Enter your guess (1-100):", min_value=1, max_value=100, step=1)
            if st.button("Submit Guess"):
                st.session_state.attempts += 1
                if guess < st.session_state.target_number:
                    st.warning("Too low!")
                elif guess > st.session_state.target_number:
                    st.warning("Too high!")
                else:
                    st.success(f"Correct! You guessed it in {st.session_state.attempts} attempts.")
                    st.session_state.pop('target_number')
                    st.session_state.pop('attempts')
        elif game_choice == "Trivia":
            st.subheader("Trivia")
            trivia_q = random.choice(TRIVIA_QUESTIONS)
            user_answer = st.text_input(trivia_q["q"])
            if st.button("Submit Answer"):
                if user_answer.strip().lower() == trivia_q["a"]:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect! The correct answer was: {trivia_q['a']}")
    elif tab == "Upload":
        st.header("Upload Content")
        upload_type = st.selectbox("What would you like to upload?", ["Quote", "Image", "Song"])
        if upload_type == "Quote":
            quote_text = st.text_area("Quote")
            author_name = st.text_input("Author")
            if st.button("Upload Quote"):
                if quote_text.strip():
                    save_quote(quote_text.strip(), author_name.strip() or "Unknown")
                    st.success("Quote uploaded!")
                else:
                    st.error("Quote text cannot be empty.")
        elif upload_type == "Image":
            image_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
            if st.button("Upload Image"):
                if image_file:
                    os.makedirs(IMAGES_FOLDER, exist_ok=True)
                    file_path = os.path.join(IMAGES_FOLDER, image_file.name)
                    with open(file_path, "wb") as f:
                        f.write(image_file.getbuffer())
                    save_image(image_file.name)
                    st.success("Image uploaded!")
                else:
                    st.error("Please select an image file.")
        elif upload_type == "Song":
            song_title = st.text_input("Song Title")
            artist_name = st.text_input("Artist")
            song_file = st.file_uploader("Choose a song file", type=["mp3", "wav"])
            if st.button("Upload Song"):
                if song_title.strip() and song_file:
                    os.makedirs(MUSIC_FOLDER, exist_ok=True)
                    file_path = os.path.join(MUSIC_FOLDER, song_file.name)
                    with open(file_path, "wb") as f:
                        f.write(song_file.getbuffer())
                    save_song(song_title.strip(), artist_name.strip() or "Unknown", song_file.name)
                    st.success("Song uploaded!")
                else:
                    st.error("Please provide a song title and select a song file.")
else:
    st.info("Please login or register to access more features.")
    menu = st.sidebar.selectbox("Menu", ["🏠 Home", "📸 Images", "🎵 Music", "⬆️ Upload", "Dashboard"])
    page = "Main" if menu == "🏠 Home" else "Dashboard" if menu == "Dashboard" else "Content"
    # --- MAIN PAGE ---
    if page == "Main":
        st.header("Welcome to Mood Minder!")
        st.markdown("Your personal space for happiness and relaxation.")
        st.markdown("Use the sidebar to navigate through quotes, images, music, and games.")
    # --- CONTENT PAGES ---
    elif page == "Content":
        # --- IMAGES PAGE ---
        if menu == "📸 Images":
            st.header("😊 Happy Images")
            if st.button("Show Random Image"):
                image = get_random_image()
                if image:
                    display_image(image)
                else:
                    st.warning("No images found. Please upload some.")
        # --- MUSIC PAGE ---
        elif menu == "🎵 Music":
            st.header("🎶 Random Happy Song")
            songs = load_songs()
            if songs and st.button("Play a random song"):
                song = random.choice(songs)
                display_song(song)
            else:
                st.warning("No songs found. Please upload some.")
        # --- UPLOAD PAGE ---
        elif menu == "⬆️ Upload":
            st.header("📂 Upload New Content")
            st.warning("Please login to upload content.")
            # Quotes
            with st.form("quote_form"):
                st.subheader("➕ Add a new quote")
                new_quote = st.text_area("Quote")
                new_author = st.text_input("Author")
                submitted = st.form_submit_button("Save Quote")
                if submitted and new_quote.strip():
                    save_quote(new_quote.strip(), new_author.strip() if new_author else "Unknown")
                    st.success("✅ Quote saved successfully!")
            # Images
            uploaded_image = st.file_uploader("➕ Upload a happy image", type=["png", "jpg", "jpeg"], key="upload_image")
            if uploaded_image is not None:
                if not os.path.exists(IMAGES_FOLDER):
                    os.makedirs(IMAGES_FOLDER)
                img_path = os.path.join(IMAGES_FOLDER, uploaded_image.name)
                with open(img_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
                save_image(uploaded_image.name)
                st.success(f"✅ Image {uploaded_image.name} uploaded successfully!")
            # Songs
            with st.form("song_form"):
                st.subheader("➕ Upload a happy song")
                song_title = st.text_input("Song Title")
                song_artist = st.text_input("Artist")
                uploaded_song = st.file_uploader("Choose a song file", type=["mp3", "wav"], key="upload_song")
                submitted = st.form_submit_button("Save Song")
                if submitted and song_title.strip() and uploaded_song is not None:
                    if not os.path.exists(MUSIC_FOLDER):
                        os.makedirs(MUSIC_FOLDER)
                    song_path = os.path.join(MUSIC_FOLDER, uploaded_song.name)
                    with open(song_path, "wb") as f:
                        f.write(uploaded_song.getbuffer())
                    save_song(song_title.strip(), song_artist.strip() if song_artist else "Unknown", uploaded_song.name)
                    st.success(f"✅ Song {song_title} uploaded successfully!")
    # --- DASHBOARD PAGE ---
    elif page == "Dashboard":
        if menu == "Dashboard":
            if current_user:
                dashboard_view(db, current_user)
            else:
                st.warning("Please login to access the dashboard.")