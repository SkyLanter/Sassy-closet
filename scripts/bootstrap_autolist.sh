#!/bin/sh
# Recreate the auto-list venv from scratch. No existing .venv or out/ required.
set -eu
cd "$(dirname "$0")/.."
rm -rf .venv
mkdir -p out
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
echo "auto-list venv ready: .venv"
echo "Run: .venv/bin/python -m pytest scripts/tests"
