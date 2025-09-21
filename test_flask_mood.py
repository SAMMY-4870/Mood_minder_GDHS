#!/usr/bin/env python3
"""
Test Flask app with mood assessment
"""
from flask import Flask, render_template, request, jsonify
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = 'test_key'

# Mock functions
def require_login():
    return True

def get_current_user():
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

@app.route("/")
def home():
    return "Flask app is running! <a href='/mood-assessment'>Test Mood Assessment</a>"

@app.route("/mood-assessment")
def mood_assessment():
    try:
        print("Mood assessment route called")
        
        if not require_login():
            return "Not logged in"
        
        user = get_current_user()
        print(f"User: {user}")
        
        # Import mood assessment
        from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
        print(f"Imported {len(HEALTH_QUESTIONS)} questions")
        
        # Get random questions
        quick_questions = mood_assessor.get_random_questions(5)
        print(f"Generated {len(quick_questions)} quick questions")
        
        return render_template("mood_assessment.html", 
                             user=user, 
                             questions=HEALTH_QUESTIONS, 
                             quick_questions=quick_questions)
        
    except Exception as e:
        print(f"Error in mood assessment route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

@app.route("/api/mood-assessment", methods=["POST"])
def api_mood_assessment():
    try:
        print("API mood assessment called")
        
        from src.mood_assessment import mood_assessor
        
        data = request.get_json()
        responses = data.get("responses", [])
        print(f"Received {len(responses)} responses")
        
        # Get analysis
        analysis = mood_assessor.get_mood_analysis(responses)
        print(f"Analysis: {analysis['mood_category']}")
        
        return jsonify({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        print(f"Error in API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    print("Starting test Flask app...")
    print("Visit: http://localhost:5001/mood-assessment")
    app.run(debug=True, port=5001)
