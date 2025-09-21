#!/usr/bin/env python3
"""
Minimal test to check mood assessment
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimal():
    try:
        print("Testing minimal imports...")
        
        # Test basic imports first
        import numpy as np
        print("✓ numpy")
        
        import pandas as pd
        print("✓ pandas")
        
        from sklearn.ensemble import RandomForestClassifier
        print("✓ sklearn")
        
        import joblib
        print("✓ joblib")
        
        from pymongo import MongoClient
        print("✓ pymongo")
        
        # Test mood assessment
        print("\nTesting mood assessment...")
        from src.mood_assessment import HEALTH_QUESTIONS
        print(f"✓ HEALTH_QUESTIONS: {len(HEALTH_QUESTIONS)} questions")
        
        from src.mood_assessment import mood_assessor
        print("✓ mood_assessor imported")
        
        # Test basic functionality
        sample_responses = [3, 4, 3, 2, 4, 3, 4, 2, 3, 4, 3, 4, 2, 4, 3, 2, 4, 3, 4, 3]
        score, category_scores = mood_assessor.calculate_mood_score(sample_responses)
        print(f"✓ Score calculated: {score}")
        
        analysis = mood_assessor.get_mood_analysis(sample_responses)
        print(f"✓ Analysis generated: {analysis['mood_category']}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_minimal()
