@echo off
REM =============================================
REM Smart Admin Assistant — Environment Setup (Windows)
REM =============================================

echo.
echo  Setting up Smart Admin Assistant...
echo  ====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [FAIL] Python not found! Install Python 3.10+ first.
    pause
    exit /b 1
)
echo  [OK] Python found

REM Create virtual environment
if not exist "venv" (
    echo  [..] Creating virtual environment...
    python -m venv venv
    echo  [OK] Virtual environment created
) else (
    echo  [OK] Virtual environment already exists
)

REM Activate
call venv\Scripts\activate.bat
echo  [OK] Virtual environment activated

REM Install dependencies
echo  [..] Installing dependencies...
pip install -r requirements.txt
echo  [OK] Dependencies installed

REM Copy .env if not exists
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo  [OK] .env created from .env.example — please update your API keys!
    )
) else (
    echo  [OK] .env already exists
)

REM Run smoke test
echo.
echo  [..] Running smoke test...
echo.
python tests\smoke_test.py

echo.
echo  Setup complete! Run 'run.bat' to start the application.
echo.
pause
