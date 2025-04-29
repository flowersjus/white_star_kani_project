#!/bin/bash

# Exit if anything fails
set -e

# Verify the virtual environment exists
if [ ! -f "kani-env/bin/python" ]; then
  echo "Virtual environment not found."
  echo "Create it with:"
  echo "  /opt/homebrew/bin/python3.11 -m venv kani-env"
  echo "  source kani-env/bin/activate"
  echo "  pip install -r requirements.txt"
  exit 1
fi

# Run the script using the venv's python
exec ./kani-env/bin/python run_kani.py
