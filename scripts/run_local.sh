#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MOCK_MODE="false"
if [[ "$1" == "--mock" ]] || [[ "$1" == "-m" ]]; then
    MOCK_MODE="true"
fi

cd "$ROOT_DIR"

export MOCK_MODE="$MOCK_MODE"
export PORT="${PORT:-8080}"
export HOST="0.0.0.0"

echo "================================================================="
echo "🚀 Starting GECX Text Streaming Cockpit BFF"
echo "👉 Mock Mode: $MOCK_MODE"
echo "👉 URL: http://localhost:$PORT"
echo "================================================================="

.venv/bin/uvicorn bff.main:app --host "$HOST" --port "$PORT" --reload
