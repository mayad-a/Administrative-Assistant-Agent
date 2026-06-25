@echo off
REM =============================================
REM Smart Admin Assistant — Run (Windows)
REM =============================================

echo.
echo  Starting Smart Admin Assistant...
echo  =================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo  [OK] Virtual environment activated
) else (
    echo  [!!] No virtual environment found. Run setup.bat first.
    pause
    exit /b 1
)

REM Run the Gradio app
echo  [..] Launching Gradio on http://localhost:7860
echo.
python app\ui.py
