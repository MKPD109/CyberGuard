@echo off
REM CyberGuard Startup Script for Windows

echo.
echo 🛡️  Starting CyberGuard...
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ Error: .env file not found!
    echo Please copy .env.example to .env and add your API keys
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run Django
echo Starting Django server...
echo Access the app at: http://localhost:8000
echo.
python manage.py runserver

pause
