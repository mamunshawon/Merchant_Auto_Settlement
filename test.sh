#!/usr/bin/env bash
set -euo pipefail

# Resolve project root to the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[$(date)] Starting Merchant_Auto_Settlement TEST run"

# Clean up any leftover chromedriver processes from previous runs
if command -v pgrep >/dev/null 2>&1; then
  if pgrep -f "chromedriver" >/dev/null 2>&1; then
    echo "[$(date)] Killing existing chromedriver processes"
    pkill -f "chromedriver" || true
  fi
else
  pkill -f "chromedriver" 2>/dev/null || true
fi

# Activate virtual environment (expected at ./myenv)
if [ -d "myenv" ] && [ -f "myenv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "myenv/bin/activate"
  echo "[$(date)] Activated virtualenv at myenv"
else
  echo "[$(date)] WARNING: virtualenv 'myenv' not found; running with system Python"
fi

# Run the dedicated test runner (uses merchant BM00RZSX00261)
python -u test_runner.py

# Deactivate virtualenv if active
if [ "${VIRTUAL_ENV-}" != "" ]; then
  deactivate || true
  echo "[$(date)] Deactivated virtualenv"
fi

# Final chromedriver cleanup just in case
if command -v pkill >/dev/null 2>&1; then
  pkill -f "chromedriver" 2>/dev/null || true
fi

echo "[$(date)] Finished Merchant_Auto_Settlement TEST run"

