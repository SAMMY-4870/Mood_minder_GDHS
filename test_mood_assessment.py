#!/usr/bin/env python3
"""
Test script for mood assessment functionality
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import numpy as np
        print("✓ numpy imported")
        
        import pandas as pd
        print("✓ pandas imported")
        
        from sklearn.ensemble import RandomForestClassifier
        print("✓ sklearn imported")
        
        import joblib
        print("✓ joblib imported")
        
        from pymongo import MongoClient
        print("✓ pymongo imported")
        
        # Test mood assessment import
        from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
        print("✓ mood_assessment imported")
        
        # Test chatbot import
        from src.gemini_chatbot import health_chatbot
        print("✓ gemini_chatbot imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_mood_assessment():
    """Test mood assessment functionality"""
    try:
        print("\nTesting mood assessment...")
        
        from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
        
        # Test questions
        print(f"✓ Found {len(HEALTH_QUESTIONS)} questions")
        
        # Test random questions
        random_questions = mood_assessor.get_random_questions(5)
        print(f"✓ Generated {len(random_questions)} random questions")
        
        # Test mood calculation with sample data
        sample_responses = [3, 4, 3, 2, 4, 3, 4, 2, 3, 4, 3, 4, 2, 4, 3, 2, 4, 3, 4, 3]
        score, category_scores = mood_assessor.calculate_mood_score(sample_responses)
        print(f"✓ Calculated mood score: {score}")
        
        # Test mood analysis
        analysis = mood_assessor.get_mood_analysis(sample_responses)
        print(f"✓ Generated analysis for category: {analysis['mood_category']}")
        
        print("✅ Mood assessment test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Mood assessment error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chatbot():
    """Test chatbot functionality"""
    try:
        print("\nTesting chatbot...")
        
        from src.gemini_chatbot import health_chatbot
        
        # Test quick responses
        quick_responses = health_chatbot.get_quick_responses("good")
        print(f"✓ Generated {len(quick_responses)} quick responses")
        
        # Test resources
        resources = health_chatbot.get_mental_health_resources("general")
        print(f"✓ Found {len(resources)} mental health resources")
        
        print("✅ Chatbot test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧠 Testing Mood Assessment System\n")
    
    # Run tests
    import_success = test_imports()
    
    if import_success:
        mood_success = test_mood_assessment()
        chatbot_success = test_chatbot()
        
        if mood_success and chatbot_success:
            print("\n🎉 All tests passed! Mood assessment should work correctly.")
        else:
            print("\n❌ Some tests failed. Check the errors above.")
    else:
        print("\n❌ Import tests failed. Install missing dependencies.")
        print("\nTo install dependencies, run:")
        print("pip install -r requirements.txt")
