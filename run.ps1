# Setup, check and reset for the labs. Windows PowerShell.
param([string]$Command = "setup")

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }

& $py -c "import sys; sys.exit(0) if sys.version_info >= (3,11) else sys.exit('Python 3.11+ required')"
& $py -c "import yaml" 2>$null
if ($LASTEXITCODE -ne 0) { & $py -m pip install -r requirements.txt }

switch ($Command) {
  "setup" {
    Write-Host ""
    Write-Host "run a module:    $py module1\run.py"
    Write-Host "check a lab:     $py module2\check.py   (modules 2 to 8)"
  }
  "check" {
    $fail = 0
    2..8 | ForEach-Object {
      & $py "module$_\check.py"
      if ($LASTEXITCODE -ne 0) { $fail = 1 }
    }
    exit $fail
  }
  "reset" { & $py scripts\reset.py }
  default { Write-Host "usage: .\run.ps1 [setup|check|reset]"; exit 1 }
}
