#!/usr/bin/env bash
# Brings the stack up. Linux and macOS. See run.ps1 for Windows.
set -euo pipefail
cd "$(dirname "$0")"

PY=${PYTHON:-python3}
command -v "$PY" >/dev/null || { echo "python3 not found"; exit 1; }

"$PY" - <<'PYCHECK'
import sys
if sys.version_info < (3, 11):
    sys.exit(f"Python 3.11+ required, found {sys.version.split()[0]}")
print(f"python {sys.version.split()[0]} ok")
PYCHECK

"$PY" -c "import yaml" 2>/dev/null || "$PY" -m pip install -r requirements.txt

case "${1:-up}" in
  up)
    echo "starting metrics server on http://127.0.0.1:8080/metrics"
    "$PY" -m substrate.metrics_server &
    echo $! > .state-pid 2>/dev/null || true
    echo
    echo "run a module:   $PY module1/run.py"
    echo "check your work: $PY module1/check.py"
    ;;
  check)
    fail=0
    for m in 1 2 3 4 5 6 7 8; do
      "$PY" "module$m/check.py" || fail=1
    done
    exit $fail
    ;;
  reset)
    "$PY" scripts/reset.py
    ;;
  down)
    [ -f .state-pid ] && kill "$(cat .state-pid)" 2>/dev/null || true
    rm -f .state-pid
    echo "stopped"
    ;;
  *)
    echo "usage: ./run.sh [up|check|reset|down]"; exit 1;;
esac
