$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m PyInstaller `
  --noconfirm `
  --onefile `
  --windowed `
  --paths "$scriptDir\src" `
  --collect-submodules x_url_ingestor `
  --name XUrlToQuartz `
  run_gui.py

Write-Host "EXE built at: $scriptDir\dist\XUrlToQuartz.exe"
