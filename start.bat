@echo off
echo ============================================
echo Starting Zoho Desk Call Ticket Processor
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy env.example to .env and configure your credentials
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting processor...
echo Press Ctrl+C to stop
echo.

python zoho_call_processor.py

pause

