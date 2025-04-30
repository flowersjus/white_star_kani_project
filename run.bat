@echo off
REM run.bat - Launches the AI DM on Windows using Command Prompt

REM Check if virtual environment exists
if not exist ".\kani-env\Scripts\activate.bat" (
    echo ❌ Virtual environment not found.
    echo To set it up, run the following:
    echo.
    echo   python -m venv kani-env
    echo   .\kani-env\Scripts\activate.bat
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Activate the virtual environment
call .\kani-env\Scripts\activate.bat

REM Run the script
python run_kani.py 