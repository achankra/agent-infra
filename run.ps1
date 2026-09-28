# Brings the stack up. Windows PowerShell.
param([string]$Command = "up")

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }

& $py -c "import sys; sys.exit(0) if sys.version_info >= (3,11) else sys.exit('Python 3.11+ required')"
& $py -c "import yaml" 2>$null
if ($LASTEXITCODE -ne 0) { & $py -m pip install -r requirements.txt }

switch ($Command) {
  "up" {
    Write-Host "starting metrics server on http://127.0.0.1:8080/metrics"
    Start-Process -NoNewWindow $py "-m","substrate.metrics_server"
    Write-Host ""
    Write-Host "run a module:    $py module1\run.py"
    Write-Host "check your work: $py module1\check.py"
  }
  "check" {
    $fail = 0
    1..8 | ForEach-Object {
      & $py "module$_\check.py"
      if ($LASTEXITCODE -ne 0) { $fail = 1 }
    }
    exit $fail
  }
  "reset" { & $py scripts\reset.py }
  "down"  { Get-Process $py -ErrorAction SilentlyContinue | Stop-Process -Force }
  default { Write-Host "usage: .\run.ps1 [up|check|reset|down]"; exit 1 }
}
