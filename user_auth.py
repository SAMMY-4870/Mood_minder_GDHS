import streamlit as st
from pymongo import MongoClient
from datetime import datetime
from hashlib import sha256

# --- DATABASE SETUP ---
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["happy_quotes_db"]

# --- HELPERS ---
def hash_password(password):
    return sha256(password.encode()).hexdigest()

def register_user(first_name, last_name, email, password):
    if db.users.find_one({"email": email}):
        st.error("Email already registered! Please login.")
        return False
    db.users.insert_one({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now()
    })
    st.success("✅ Registration successful! You can now log in.")
    return True

def login_user(email, password):
    user = db.users.find_one({"email": email})
    if user and user["password"] == hash_password(password):
        st.success(f"Welcome back, {user['first_name']}!")
        return user
    else:
        st.error("Invalid email or password.")
        return None
