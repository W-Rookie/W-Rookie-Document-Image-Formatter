#!/usr/bin/env bash

set -u
cd -- "$(dirname -- "$0")"

ERROR_LOG="$PWD/setup-error.log"
PYTHON_BIN=""

pause_terminal() {
  if [[ -t 0 ]]; then
    read -r -p "Press Enter to close this setup window..." _answer
  fi
}

fail_setup() {
  local message="$1"
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$message" >"$ERROR_LOG"
  printf '\n[ERROR] %s\nError details: %s\n\n' "$message" "$ERROR_LOG"
  pause_terminal
  exit 1
}

printf '%s\n' '============================================================'
printf '%s\n' ' W-Rookie - macOS/Linux first-time setup'
printf '%s\n\n' '============================================================'

for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && \
    "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  fail_setup "Python 3.10 or newer was not found."
fi

if ! "$PYTHON_BIN" -c 'import tkinter' >/dev/null 2>&1; then
  printf '%s\n' 'Tkinter is required for the GUI.'
  if [[ "$(uname -s)" == "Linux" ]]; then
    printf '%s\n' 'Install it with your package manager, for example: sudo apt install python3-tk'
  else
    printf '%s\n' 'Install a current Python from https://www.python.org/downloads/macos/'
  fi
  fail_setup "Python Tkinter GUI support was not found."
fi

printf '[1/4] Python found: '
"$PYTHON_BIN" --version

if [[ ! -x .venv/bin/python ]]; then
  printf '%s\n' '[2/4] Creating a private Python environment...'
  "$PYTHON_BIN" -m venv .venv || fail_setup "Virtual environment creation failed."
else
  printf '%s\n' '[2/4] Existing private Python environment found.'
fi

printf '%s\n' '[3/4] Updating the installer...'
.venv/bin/python -m pip install --upgrade pip || fail_setup "pip upgrade failed."

printf '%s\n' '[4/4] Installing W-Rookie and security components...'
.venv/bin/python -m pip install -e . || fail_setup "W-Rookie installation failed."
.venv/bin/python -c 'import docpicalign, defusedxml, olefile, tkinter' || \
  fail_setup "Final import validation failed."

rm -f -- "$ERROR_LOG"
printf '\n%s\n' '============================================================'
printf '%s\n' ' Setup completed successfully.'
printf '%s\n' ' Next: run ./run.sh (or double-click run.command on macOS).'
printf '%s\n\n' '============================================================'
pause_terminal
