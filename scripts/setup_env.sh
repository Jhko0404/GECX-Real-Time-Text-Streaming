#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

echo "================================================================="
echo "[GECX] 가상환경 및 의존성 구성"
echo "================================================================="

# 1. Python Virtual Environment
echo "[1/3] Python 가상환경 구성 중..."
if [ ! -d ".venv" ]; then
    if command -v uv &> /dev/null; then
        uv venv .venv
        uv pip install -r requirements.txt
    elif command -v python3 &> /dev/null; then
        python3 -m venv .venv
        .venv/bin/pip install --upgrade pip
        .venv/bin/pip install -r requirements.txt
    else
        echo "Error: python3 또는 uv를 찾을 수 없습니다."
        exit 1
    fi
else
    echo "기존 가상환경(.venv)을 사용합니다."
fi

# 2. Web Frontend Dependencies
echo "[2/3] Node.js 프론트엔드 패키지 설치 중..."
cd "$ROOT_DIR/web"
if [ ! -d "node_modules" ]; then
    npm install
fi

# 3. Build Web Assets
echo "[3/3] 프론트엔드 정적 에셋 빌드 중..."
npm run build

echo "================================================================="
echo "환경 구성이 완료되었습니다."
echo "로컬 서버 실행: ./scripts/run_local.sh"
echo "================================================================="
