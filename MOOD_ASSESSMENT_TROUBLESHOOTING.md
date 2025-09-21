# 🧠 Mood Assessment Troubleshooting Guide

## 🚨 Common Issues and Solutions

### **Issue 1: Import Errors**
**Error**: `ModuleNotFoundError: No module named 'sklearn'` or similar

**Solution**:
```bash
pip install scikit-learn==1.7.2
pip install google-generativeai==0.3.2
pip install joblib==1.5.2
pip install numpy pandas pymongo
```

### **Issue 2: Flask App Won't Start**
**Error**: `ImportError` when starting Flask app

**Solution**:
1. Check if all dependencies are installed
2. Run the test script: `python test_mood_simple.py`
3. Check for syntax errors in the files

### **Issue 3: Template Not Found**
**Error**: `TemplateNotFound: mood_assessment.html`

**Solution**:
1. Ensure the template file exists in `templates/mood_assessment.html`
2. Check file permissions
3. Verify the template extends `base.html` correctly

### **Issue 4: Database Connection Issues**
**Error**: `pymongo.errors.ServerSelectionTimeoutError`

**Solution**:
1. Check MongoDB connection string
2. Ensure internet connection
3. Verify MongoDB Atlas credentials

### **Issue 5: JavaScript Errors**
**Error**: Frontend not working, buttons not responding

**Solution**:
1. Check browser console for JavaScript errors
2. Ensure jQuery and Bootstrap are loaded
3. Check for template syntax errors

## 🔧 Step-by-Step Debugging

### **Step 1: Test Dependencies**
```bash
python test_mood_simple.py
```
This will test if all required modules can be imported.

### **Step 2: Test Flask App**
```bash
python test_flask_mood.py
```
This will start a test Flask app on port 5001 to test the mood assessment route.

### **Step 3: Check Main App**
```bash
python web_app.py
```
Start the main Flask app and check for any startup errors.

### **Step 4: Test in Browser**
1. Go to `http://localhost:5000/mood-assessment`
2. Check browser console for errors
3. Try submitting a test assessment

## 🐛 Debugging Commands

### **Check Python Version**
```bash
python --version
```
Should be Python 3.7 or higher.

### **Check Installed Packages**
```bash
pip list | grep -E "(scikit|google|joblib|numpy|pandas|pymongo)"
```

### **Test MongoDB Connection**
```python
from pymongo import MongoClient
client = MongoClient("your_mongodb_uri")
print("MongoDB connected successfully")
```

### **Test Mood Assessment Module**
```python
from src.mood_assessment import mood_assessor, HEALTH_QUESTIONS
print(f"Questions: {len(HEALTH_QUESTIONS)}")
print("Mood assessment module loaded successfully")
```

## 🚀 Quick Fixes

### **Fix 1: Reinstall Dependencies**
```bash
pip uninstall scikit-learn google-generativeai joblib
pip install scikit-learn==1.7.2 google-generativeai==0.3.2 joblib==1.5.2
```

### **Fix 2: Clear Python Cache**
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### **Fix 3: Restart Flask App**
```bash
# Kill any running Flask processes
pkill -f "python.*web_app.py"
# Start fresh
python web_app.py
```

### **Fix 4: Check File Permissions**
```bash
chmod 644 templates/mood_assessment.html
chmod 644 src/mood_assessment.py
```

## 📋 Checklist

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Python version 3.7+ (`python --version`)
- [ ] MongoDB connection working
- [ ] Template file exists (`templates/mood_assessment.html`)
- [ ] No syntax errors in Python files
- [ ] Flask app starts without errors
- [ ] Browser console shows no JavaScript errors
- [ ] Test assessment can be submitted

## 🆘 Still Not Working?

If the mood assessment still doesn't work:

1. **Run the test script**: `python test_mood_simple.py`
2. **Check the error message** and share it
3. **Try the test Flask app**: `python test_flask_mood.py`
4. **Check browser console** for JavaScript errors
5. **Verify all files exist** and have correct permissions

## 📞 Getting Help

If you're still having issues, please share:
1. The exact error message you're seeing
2. Output from `python test_mood_simple.py`
3. Your Python version (`python --version`)
4. Your operating system
5. Any error messages from the browser console

This will help identify the specific issue and provide a targeted solution.
