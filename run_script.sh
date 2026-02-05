#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/qupid-app"

echo "== Qupid: setup backend =="
python3 -m venv "$ROOT_DIR/.venv"
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
python3 -m pip install --upgrade pip
python3 -m pip install -r "$BACKEND_DIR/requirements.txt"

echo "== Qupid: setup frontend =="
cd "$FRONTEND_DIR"
npm install
npm run build

echo "== Qupid: start backend =="
cd "$ROOT_DIR"
trap 'kill $(jobs -p) 2>/dev/null || true' EXIT

python3 "$BACKEND_DIR/app.py" &
BACK_PID=$!

echo "Backend PID: $BACK_PID"
echo "App is served at: http://localhost:5000"

wait
