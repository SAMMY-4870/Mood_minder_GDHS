import streamlit as st
import random
import os
from PIL import Image
from pymongo import MongoClient
from user_dashboard import dashboard_view  # Dashboard function
basedir = os.path.abspath(os.path.dirname(__file__))

# --- CONFIG ---
IMAGES_FOLDER = "data/images/happy"
MUSIC_FOLDER = "data/music"

# --- DATABASE SETUP ---
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://Samarth_90:Samarth%409090@moodminder.dci9zcf.mongodb.net/?retryWrites=true&w=majority"
)
client = MongoClient(MONGO_URI)
db = client["happy_quotes_db"]

# --- USER AUTH HELPERS ---
def register_user(first_name, last_name, email, password):
    """Register a new user if email is not taken."""
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
    """Check user credentials and return user info."""
    user = db.users.find_one({"email": email, "password": password}, {"_id": 0})
    return user

# --- CONTENT HELPERS ---
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
        if password != confirm_password:
            st.sidebar.error("Passwords do not match!")
        elif not (first_name and last_name and email and password):
            st.sidebar.error("Please fill in all fields.")
        else:
            success, msg = register_user(first_name, last_name, email, password)
            if success:
                st.sidebar.success(msg)
            else:
                st.sidebar.error(msg)

elif auth_option == "Login":
    st.sidebar.subheader("Login to your account")
    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Login"):
        user = login_user(email, password)
        if user:
            current_user = user
            st.sidebar.success(f"Welcome back, {user['first_name']}!")
        else:
            st.sidebar.error("Invalid email or password.")

# --- MAIN NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Quotes & Media", "Dashboard"], key="main_nav")

# --- HOME PAGE ---
if page == "Home":
    st.title("😊 Welcome to the Happy Quotes App!")
    if current_user:
        st.write(f"Logged in as: {current_user['first_name']} {current_user['last_name']}")
    st.write("Use the sidebar to navigate through quotes, images, music, or your activity dashboard.")

# --- QUOTES & MEDIA PAGE ---
elif page == "Quotes & Media":
    menu = st.sidebar.radio(
        "Select Content", ["📖 Quotes", "📸 Images", "🎵 Music", "⬆️ Upload"], key="media_nav"
    )

    # --- QUOTES PAGE ---
    if menu == "📖 Quotes":
        st.header("✨ Random Quote")
        quotes = load_quotes()
        if quotes and st.button("Show me a quote", key="show_quote"):
            row = random.choice(quotes)
            st.success(f"**{row['quote']}** — *{row['author']}*")

    # --- IMAGES PAGE ---
    elif menu == "📸 Images":
        st.header("✨ Random Image")
        if st.button("Show me an image", key="show_image"):
            img = get_random_image()
            if img:
                st.image(img, caption="Here's something happy 😊", use_column_width=True)
            else:
                st.warning("No images found. Please upload some.")

    # --- MUSIC PAGE ---
    elif menu == "🎵 Music":
        st.header("🎶 Random Happy Song")
        songs = load_songs()
        if songs and st.button("Play a random song", key="play_song"):
            row = random.choice(songs)
            st.write(f"**{row['title']}** — *{row['artist']}*")
            file_path = os.path.join(MUSIC_FOLDER, row["file"])
            if os.path.exists(file_path):
                audio_file = open(file_path, "rb")
                st.audio(audio_file.read(), format="audio/mp3")

    # --- UPLOAD PAGE ---
    elif menu == "⬆️ Upload":
        st.header("📂 Upload New Content")
        # Only allow upload if logged in
        if not current_user:
            st.warning("Please login to upload content.")
        else:
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
            uploaded_song = st.file_uploader("➕ Upload a happy song", type=["mp3", "wav"], key="upload_song")
            song_title = st.text_input("Song Title", key="song_title")
            song_artist = st.text_input("Artist", key="song_artist")
            if uploaded_song is not None and song_title.strip():
                if not os.path.exists(MUSIC_FOLDER):
                    os.makedirs(MUSIC_FOLDER)
                song_path = os.path.join(MUSIC_FOLDER, uploaded_song.name)
                with open(song_path, "wb") as f:
                    f.write(uploaded_song.getbuffer())
                save_song(song_title.strip(), song_artist.strip() if song_artist else "Unknown", uploaded_song.name)
                st.success(f"✅ Song '{song_title}' uploaded successfully!")

# --- DASHBOARD PAGE ---
elif page == "Dashboard":
    dashboard_view(current_user=current_user)
