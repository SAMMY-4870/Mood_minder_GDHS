# Windows Troubleshooting Guide

## 🚨 Common Windows Flask Issues & Solutions

### Issue: WinError 10038 - Socket Error
**Error**: `OSError: [WinError 10038] An operation was attempted on something that is not a socket`

**Cause**: Windows socket handling issues with Flask's development server and auto-reload feature.

### ✅ **SOLUTIONS (Try in order):**

## 1. **Quick Fix - Use Stable Runner**
```bash
python run_app_stable.py
```
This disables auto-reload and debug mode for better Windows compatibility.

## 2. **Production Mode - Use Waitress**
```bash
python run_app_production.py
```
Uses Waitress WSGI server instead of Flask's development server.

## 3. **Windows Batch File**
Double-click `start_app.bat` for automatic configuration.

## 4. **Manual Environment Setup**
```bash
# Set environment variables
set TF_ENABLE_ONEDNN_OPTS=0
set TF_CPP_MIN_LOG_LEVEL=2
set FLASK_ENV=production

# Run with specific settings
python -c "from web_app import app; app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)"
```

## 5. **Alternative Port**
If port 5000 is busy:
```bash
python -c "from web_app import app; app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False, threaded=True)"
```

---

## 🔧 **Additional Fixes:**

### Fix 1: Disable TensorFlow File Monitoring
Add to the top of `web_app.py`:
```python
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

### Fix 2: Use Different WSGI Server
Install and use Gunicorn or Waitress:
```bash
pip install waitress
python run_app_production.py
```

### Fix 3: Disable Windows Defender Real-time Protection
Temporarily disable Windows Defender for the project folder to prevent file monitoring conflicts.

### Fix 4: Run as Administrator
Right-click Command Prompt → "Run as administrator" and try again.

---

## 🐛 **Debug Steps:**

1. **Check if port is in use:**
   ```bash
   netstat -ano | findstr :5000
   ```

2. **Kill process using port:**
   ```bash
   taskkill /PID <PID_NUMBER> /F
   ```

3. **Check Python version:**
   ```bash
   python --version
   ```

4. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

---

## 🚀 **Recommended Startup Sequence:**

1. **First try:** `python run_app_stable.py`
2. **If that fails:** `python run_app_production.py`
3. **If still issues:** Use the batch file `start_app.bat`
4. **Last resort:** Manual environment setup

---

## 📱 **Access the App:**
Once running successfully, open your browser and go to:
- **http://127.0.0.1:5000** (default)
- **http://127.0.0.1:8080** (if using alternative port)

---

## ⚠️ **Important Notes:**

- **Auto-reload is disabled** in stable mode - restart manually after code changes
- **TensorFlow warnings** are suppressed but the app still works
- **Windows Defender** may need to allow Python through firewall
- **Antivirus software** might interfere with file monitoring

---

## 🆘 **Still Having Issues?**

1. Check Windows Event Viewer for detailed error logs
2. Try running in a virtual environment
3. Update Python to latest version
4. Check if any antivirus is blocking the application
5. Try running from a different directory

---

## 📞 **Quick Commands:**

```bash
# Install waitress if needed
pip install waitress

# Run stable version
python run_app_stable.py

# Run production version
python run_app_production.py

# Check what's using port 5000
netstat -ano | findstr :5000
```
