#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================================="
echo "🛠️ Setting up GECX Text Streaming Environment"
echo "================================================================="

cd "$ROOT_DIR"

# 1. Setup Python venv
echo "[1/3] Setting up Python virtual environment..."
if command -v uv &> /dev/null; then
    uv venv .venv
    uv pip install -r requirements.txt
elif command -v /usr/local/google/home/junghyunko/.local/bin/uv &> /dev/null; then
    /usr/local/google/home/junghyunko/.local/bin/uv venv .venv
    /usr/local/google/home/junghyunko/.local/bin/uv pip install -r requirements.txt
else
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

# 2. Setup Node / Web dependencies
echo "[2/3] Installing Web Frontend dependencies..."
cd "$ROOT_DIR/web"
npm install

# 3. Build Frontend
echo "[3/3] Building Web Frontend assets..."
npm run build

echo "================================================================="
echo "✅ Environment setup complete!"
echo "👉 Start locally: ./scripts/run_local.sh"
echo "================================================================="
