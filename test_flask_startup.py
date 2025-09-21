#!/usr/bin/env python3
"""
Test Flask app startup and mood assessment route
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_flask_startup():
    """Test if Flask app can start and mood assessment route works"""
    try:
        print("🔍 Testing Flask app startup...")
        
        # Import the web_app module
        import web_app
        
        # Get the Flask app
        app = web_app.app
        print("✓ Flask app object retrieved")
        
        # Test if mood assessment route is registered
        with app.app_context():
            rules = [rule.rule for rule in app.url_map.iter_rules()]
            if '/mood-assessment' in rules:
                print("✓ mood-assessment route is registered")
            else:
                print("❌ mood-assessment route not found")
                print("Available routes:", rules)
                return False
        
        print("✅ Flask app startup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app startup error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_route_functions():
    """Test if route functions exist and are callable"""
    try:
        print("\n🔍 Testing route functions...")
        
        import web_app
        
        # Check if mood assessment function exists
        if hasattr(web_app, 'mood_assessment'):
            print("✓ mood_assessment function exists")
        else:
            print("❌ mood_assessment function not found")
            return False
        
        # Check if API function exists
        if hasattr(web_app, 'api_mood_assessment'):
            print("✓ api_mood_assessment function exists")
        else:
            print("❌ api_mood_assessment function not found")
            return False
        
        print("✅ Route functions exist!")
        return True
        
    except Exception as e:
        print(f"❌ Route functions error: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Testing Flask App Startup\n")
    
    # Run tests
    startup_ok = test_flask_startup()
    functions_ok = test_route_functions()
    
    print("\n📊 Test Summary:")
    print(f"Flask Startup: {'✅' if startup_ok else '❌'}")
    print(f"Route Functions: {'✅' if functions_ok else '❌'}")
    
    if startup_ok and functions_ok:
        print("\n🎉 Flask app should work correctly!")
        print("\n💡 Try running: python web_app.py")
        print("Then visit: http://localhost:5000/mood-assessment")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
