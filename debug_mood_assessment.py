#!/usr/bin/env python3
"""
Debug script to test mood assessment route
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = 'debug_key'

# Mock user for testing
def get_current_user():
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

def require_login():
    return True  # Always return True for testing

@app.route("/mood-assessment")
def mood_assessment():
    print("Mood assessment route called")
    
    if not require_login():
        return redirect(url_for("login"))
    
    try:
        user = get_current_user()
        print(f"User: {user}")
        
        # Try to import mood assessment
        from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
        print(f"Imported {len(HEALTH_QUESTIONS)} questions")
        
        # Get 5 random questions for quick assessment
        quick_questions = mood_assessor.get_random_questions(5)
        print(f"Generated {len(quick_questions)} quick questions")
        
        return render_template("mood_assessment.html", user=user, questions=HEALTH_QUESTIONS, quick_questions=quick_questions)
        
    except Exception as e:
        print(f"Error in mood assessment route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500

@app.route("/api/mood-assessment", methods=["POST"])
def api_mood_assessment():
    print("API mood assessment called")
    
    try:
        from src.mood_assessment import mood_assessor
        
        data = request.get_json()
        responses = data.get("responses", [])
        is_quick = data.get("is_quick", False)
        
        print(f"Received responses: {responses}")
        
        # Get analysis
        analysis = mood_assessor.get_mood_analysis(responses)
        print(f"Analysis: {analysis['mood_category']}")
        
        return jsonify({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        print(f"Error in API mood assessment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("Starting debug server...")
    app.run(debug=True, port=5001)
