#!/bin/bash

# Exit if anything fails
set -e

# Function to check if we're on Windows
is_windows() {
    case "$(uname -s)" in
        CYGWIN*|MINGW*|MSYS*) return 0 ;;
        *) return 1 ;;
    esac
}

# Set paths based on OS
if is_windows; then
    VENV_PYTHON="kani-env/Scripts/python.exe"
    VENV_ACTIVATE="kani-env/Scripts/activate"
else
    VENV_PYTHON="kani-env/bin/python"
    VENV_ACTIVATE="kani-env/bin/activate"
fi

# Verify the virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Virtual environment not found."
    echo "Create it with:"
    echo "  python3 -m venv kani-env"
    if is_windows; then
        echo "  kani-env\\Scripts\\activate"
    else
        echo "  source kani-env/bin/activate"
    fi
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Run the script using the venv's python
exec "$VENV_PYTHON" run_kani.py
