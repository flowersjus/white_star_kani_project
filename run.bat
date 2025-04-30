@echo off
REM run.bat - Launches the AI DM on Windows using Command Prompt

REM Check if virtual environment exists
if not exist "kani-env\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Create it with:
    echo   python -m venv kani-env
    echo   kani-env\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Run the script using the venv's python
"kani-env\Scripts\python.exe" run_kani.py 