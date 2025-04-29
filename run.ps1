# run.ps1 - Launches the AI DM on Windows

# Stop on error
$ErrorActionPreference = "Stop"

# Check if virtual environment exists
if (-Not (Test-Path ".\kani-env\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found."
    Write-Host "To set it up, run the following:"
    Write-Host ""
    Write-Host "  python -m venv kani-env"
    Write-Host "  .\kani-env\Scripts\Activate.ps1"
    Write-Host "  pip install -r requirements.txt"
    exit 1
}

# Activate the virtual environment
& .\kani-env\Scripts\Activate.ps1

# Run the script
python run_kani.py
