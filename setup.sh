#!/usr/bin/env bash
set -euo pipefail

echo "Setting up Python venv and installing requirements..."

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment at .venv"
  python3 -m venv .venv
else
  echo "Found existing .venv"
fi

VENV_PYTHON=".venv/bin/python"

echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

echo "Installing packages from requirements.txt..."
"$VENV_PYTHON" -m pip install -r requirements.txt

echo ""
echo "Done. To activate the venv for development:"
echo "  source .venv/bin/activate"
