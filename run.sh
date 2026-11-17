#!/usr/bin/env bash

set -u
cd -- "$(dirname -- "$0")"

if [[ ! -x .venv/bin/python ]]; then
  printf '%s\n\n' '[W-Rookie] First-time setup is required.'
  ./setup.sh || exit 1
fi

if ! .venv/bin/python -c 'import docpicalign, defusedxml, olefile, tkinter' >/dev/null 2>&1; then
  printf '%s\n' '[ERROR] The installation is incomplete or damaged.'
  printf '%s\n' 'Run ./setup.sh again. If it still fails, rename the .venv folder first.'
  exit 1
fi

exec .venv/bin/python -m docpicalign
