@echo off
echo Starting Mental Health App...
echo.

REM Set environment variables
set TF_ENABLE_ONEDNN_OPTS=0
set TF_CPP_MIN_LOG_LEVEL=2
set FLASK_ENV=production

echo Environment configured for Windows compatibility
echo.

REM Try to run the stable version first
echo Attempting to start with stable configuration...
python run_app_stable.py

REM If that fails, try the production version
if errorlevel 1 (
    echo.
    echo Stable version failed, trying production version...
    python run_app_production.py
)

pause
