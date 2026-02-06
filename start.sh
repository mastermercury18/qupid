#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

# activate the venv created during build (Render persists it between build/start on the same deploy)
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

# IMPORTANT: bind to Render's port
export PORT="${PORT:-5000}"

exec python "$BACKEND_DIR/app.py"
