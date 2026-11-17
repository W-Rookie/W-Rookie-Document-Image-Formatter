#!/usr/bin/env bash

set -euo pipefail
cd -- "$(dirname -- "$0")"

if [[ ! -x .venv/bin/python ]]; then
  ./setup.sh
fi

.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m PyInstaller --noconfirm --clean --windowed --name W-Rookie --paths src --collect-data docpicalign launcher.py

printf '\nBuild complete in the dist directory.\n'
