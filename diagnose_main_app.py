#!/usr/bin/env python3
"""
Diagnose the main Flask app for mood assessment issues
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_app_imports():
    """Test if the main app can import all required modules"""
    try:
        print("🔍 Testing main app imports...")
        
        # Test basic Flask imports
        from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, send_file, flash, jsonify
        print("✓ Flask imports successful")
        
        # Test MongoDB
        from pymongo import MongoClient
        print("✓ MongoDB import successful")
        
        # Test mood assessment
        from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
        print("✓ Mood assessment import successful")
        
        # Test chatbot
        from src.gemini_chatbot import health_chatbot
        print("✓ Chatbot import successful")
        
        # Test notifications
        from src.notifications import check_achievements, get_motivational_message, get_progress_insights, save_notification, get_user_notifications, get_weekly_progress_summary
        print("✓ Notifications import successful")
        
        print("✅ All main app imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_app_loading():
    """Test if web_app.py can be loaded"""
    try:
        print("\n🔍 Testing web_app.py loading...")
        
        # Import the web_app module
        import web_app
        print("✓ web_app.py loaded successfully")
        
        # Check if the app object exists
        if hasattr(web_app, 'app'):
            print("✓ Flask app object found")
        else:
            print("❌ Flask app object not found")
            return False
        
        # Check if mood assessment route exists
        if hasattr(web_app, 'mood_assessment'):
            print("✓ mood_assessment route found")
        else:
            print("❌ mood_assessment route not found")
            return False
        
        print("✅ web_app.py loading successful!")
        return True
        
    except Exception as e:
        print(f"❌ web_app.py loading error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_rendering():
    """Test if the mood assessment template can be rendered"""
    try:
        print("\n🔍 Testing template rendering...")
        
        from flask import Flask
        from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
        
        app = Flask(__name__)
        
        with app.app_context():
            # Test template rendering
            template = app.jinja_env.get_template('mood_assessment.html')
            print("✓ Template found")
            
            # Test rendering with sample data
            user = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}
            quick_questions = mood_assessor.get_random_questions(5)
            
            rendered = template.render(user=user, questions=HEALTH_QUESTIONS, quick_questions=quick_questions)
            print("✓ Template rendered successfully")
            
        print("✅ Template rendering successful!")
        return True
        
    except Exception as e:
        print(f"❌ Template rendering error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    try:
        print("\n🔍 Testing database connection...")
        
        from pymongo import MongoClient
        
        MONGO_URI = "mongodb+srv://Samarth_90:Samarth%409090@moodminder.dci9zcf.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(MONGO_URI)
        db = client["happy_quotes_db"]
        
        # Test connection
        client.admin.command('ping')
        print("✓ Database connection successful")
        
        # Test mood assessments collection
        collections = db.list_collection_names()
        print(f"✓ Found {len(collections)} collections")
        
        print("✅ Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Diagnosing Main Flask App\n")
    
    # Run all tests
    imports_ok = test_main_app_imports()
    app_loading_ok = test_web_app_loading()
    template_ok = test_template_rendering()
    db_ok = test_database_connection()
    
    print("\n📊 Diagnosis Summary:")
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"App Loading: {'✅' if app_loading_ok else '❌'}")
    print(f"Template: {'✅' if template_ok else '❌'}")
    print(f"Database: {'✅' if db_ok else '❌'}")
    
    if all([imports_ok, app_loading_ok, template_ok, db_ok]):
        print("\n🎉 All tests passed! The main app should work correctly.")
        print("\n💡 Try running: python web_app.py")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("\n💡 Common solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check file permissions")
        print("3. Restart your terminal/IDE")
