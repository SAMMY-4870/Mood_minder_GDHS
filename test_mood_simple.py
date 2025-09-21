#!/usr/bin/env python3
"""
Simple test for mood assessment functionality
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mood_assessment():
    try:
        print("🧠 Testing Mood Assessment Module...")
        
        # Test basic imports
        print("1. Testing basic imports...")
        import numpy as np
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        import joblib
        from pymongo import MongoClient
        print("✓ All basic imports successful")
        
        # Test mood assessment import
        print("2. Testing mood assessment import...")
        from src.mood_assessment import HEALTH_QUESTIONS, mood_assessor
        print(f"✓ Found {len(HEALTH_QUESTIONS)} health questions")
        
        # Test mood calculation
        print("3. Testing mood calculation...")
        sample_responses = [3, 4, 3, 2, 4, 3, 4, 2, 3, 4, 3, 4, 2, 4, 3, 2, 4, 3, 4, 3]
        score, category_scores = mood_assessor.calculate_mood_score(sample_responses)
        print(f"✓ Mood score calculated: {score}")
        
        # Test mood analysis
        print("4. Testing mood analysis...")
        analysis = mood_assessor.get_mood_analysis(sample_responses)
        print(f"✓ Mood analysis generated: {analysis['mood_category']}")
        
        # Test random questions
        print("5. Testing random questions...")
        random_questions = mood_assessor.get_random_questions(5)
        print(f"✓ Generated {len(random_questions)} random questions")
        
        print("\n🎉 All tests passed! Mood assessment module is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 Solution: Install missing dependencies with:")
        print("pip install scikit-learn google-generativeai joblib numpy pandas pymongo")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_mood_assessment()
