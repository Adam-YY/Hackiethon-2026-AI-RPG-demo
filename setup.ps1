$ErrorActionPreference = "Stop"

Write-Host "Setting up Python venv and installing requirements..."

if (-Not (Test-Path -LiteralPath ".venv")) {
  Write-Host "Creating virtual environment at .venv"
  if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -m venv .venv
  } else {
    python -m venv .venv
  }
} else {
  Write-Host "Found existing .venv"
}

$venvPython = Join-Path ".venv" "Scripts\python.exe"

Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip

Write-Host "Installing packages from requirements.txt..."
& $venvPython -m pip install -r requirements.txt

Write-Host ""
Write-Host "Done. To activate the venv for development:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
