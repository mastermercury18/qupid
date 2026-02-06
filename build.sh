#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN=python3.10

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/qupid-app"

echo "== Qupid: setup backend (Python 3.10) =="
"$PYTHON_BIN" -m venv "$ROOT_DIR/.venv"
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
python --version
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

echo "== Qupid: setup frontend =="
cd "$FRONTEND_DIR"
npm install
npm run build

echo "== Build complete =="
