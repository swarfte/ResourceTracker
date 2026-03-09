@echo off
REM ResourceTracker Launcher
REM =========================

echo Starting ResourceTracker...
echo The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C in this window to stop the application
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo WARNING: Virtual environment not found, using system Python
)

REM Run Streamlit
streamlit run app.py

pause
