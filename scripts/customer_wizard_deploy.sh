#!/bin/bash
set -e

# ==============================================================================
# GECX Real-Time Text Streaming - Customer Deployment Wizard
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

echo "================================================================="
echo "[GECX] 고객사 환경 리소스 배포 마법사"
echo "================================================================="
echo "Google Cloud Customer Engagement Suite (CES) 텍스트 스트리밍 솔루션을"
echo "고객사 GCP 프로젝트에 구성 및 배포합니다."
echo "================================================================="
echo ""

# ------------------------------------------------------------------------------
# 1단계: gcloud CLI 및 로그인 상태 확인
# ------------------------------------------------------------------------------
echo "[1/6] Google Cloud CLI 및 인증 상태 확인 중..."
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI가 설치되어 있지 않습니다."
    echo "Google Cloud SDK를 먼저 설치해주세요: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "로그인된 gcloud 계정이 없습니다. 콘솔 로그인을 시작합니다..."
    gcloud auth login
    gcloud auth application-default login
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
fi
echo "인증 계정 확인 완료: $ACTIVE_ACCOUNT"
echo ""

# ------------------------------------------------------------------------------
# 2단계: 고객사 환경 정보 대화형 수집
# ------------------------------------------------------------------------------
echo "[2/6] 고객사 GCP 환경 정보 수집"
DEFAULT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "gemeni-workshop")

read -p "1) GCP Project ID [기본값: $DEFAULT_PROJECT]: " INPUT_PROJECT
PROJECT_ID="${INPUT_PROJECT:-$DEFAULT_PROJECT}"

read -p "2) GECX Location (us 또는 global) [기본값: us]: " INPUT_LOCATION
GCP_LOCATION="${INPUT_LOCATION:-us}"

read -p "3) Cloud Run 배포 Region [기본값: us-central1]: " INPUT_REGION
SERVICE_REGION="${INPUT_REGION:-us-central1}"

read -p "4) CX Agent Studio App ID [기본값: 8f0230a9-836f-4795-b57a-0f604540b614]: " INPUT_APP_ID
APP_ID="${INPUT_APP_ID:-8f0230a9-836f-4795-b57a-0f604540b614}"

read -p "5) Agent Deployment ID [기본값: 0b7d820b-375b-4333-b2ed-474eb0b070a9]: " INPUT_DEP_ID
DEPLOYMENT_ID="${INPUT_DEP_ID:-0b7d820b-375b-4333-b2ed-474eb0b070a9}"

read -p "6) Agent 이름 [기본값: pre_routing_test_agent]: " INPUT_APP_NAME
APP_NAME="${INPUT_APP_NAME:-pre_routing_test_agent}"

SERVICE_NAME="GECX-Real-Time-Text-Streaming"
SA_NAME="gecx-bff-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
JWT_SECRET=$(openssl rand -hex 16 2>/dev/null || echo "GECX-Real-Time-Text-Streaming-secret-$(date +%s)")

echo ""
echo "-----------------------------------------------------------------"
echo "수집된 환경 설정 요약:"
echo "   - Project ID:       $PROJECT_ID"
echo "   - GECX Location:    $GCP_LOCATION"
echo "   - Cloud Run Region: $SERVICE_REGION"
echo "   - App ID:           $APP_ID"
echo "   - Deployment ID:    $DEPLOYMENT_ID"
echo "   - Service Name:     $SERVICE_NAME"
echo "   - Service Account:  $SA_EMAIL"
echo "-----------------------------------------------------------------"
read -p "위 설정으로 배포를 진행하시겠습니까? (Y/n): " CONFIRM
if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then
    echo "배포가 취소되었습니다."
    exit 0
fi
echo ""

# ------------------------------------------------------------------------------
# 3단계: .env 파일 생성
# ------------------------------------------------------------------------------
echo "[3/6] .env 환경 설정 파일 생성 중..."
cat << EOF_ENV > .env
GCP_PROJECT_ID="$PROJECT_ID"
GCP_LOCATION="$GCP_LOCATION"
SERVICE_REGION="$SERVICE_REGION"

DEFAULT_APP_ID="$APP_ID"
DEFAULT_APP_NAME="$APP_NAME"
DEFAULT_DEPLOYMENT_ID="$DEPLOYMENT_ID"

HOST="0.0.0.0"
PORT=8080
JWT_SECRET_KEY="$JWT_SECRET"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_SECONDS=60
LOG_LEVEL="INFO"
MOCK_MODE=false
EOF_ENV
echo "환경 설정 파일 생성 완료."
echo ""

# ------------------------------------------------------------------------------
# 4단계: 필수 GCP API 활성화
# ------------------------------------------------------------------------------
echo "[4/6] 필수 Google Cloud API 활성화 중..."
gcloud services enable \
    run.googleapis.com \
    ces.googleapis.com \
    storage.googleapis.com \
    cloudbuild.googleapis.com \
    iam.googleapis.com \
    --project="$PROJECT_ID"
echo "API 활성화 완료."
echo ""

# ------------------------------------------------------------------------------
# 5단계: 전용 서비스 계정 생성 및 IAM 권한 부여
# ------------------------------------------------------------------------------
echo "[5/6] Cloud Run 전용 서비스 계정 및 IAM 권한 설정 중..."
if ! gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    echo "서비스 계정 생성: $SA_EMAIL"
    gcloud iam service-accounts create "$SA_NAME" \
        --display-name="GECX BFF Service Account" \
        --project="$PROJECT_ID"
fi

echo "IAM 역할 부여 중 (roles/ces.client, roles/storage.objectViewer, roles/logging.logWriter)..."
for ROLE in "roles/ces.client" "roles/storage.objectViewer" "roles/logging.logWriter"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="$ROLE" \
        --condition=None --quiet >/dev/null
done
echo "IAM 권한 구성 완료."
echo ""

# ------------------------------------------------------------------------------
# 6단계: 프론트엔드 빌드 및 Cloud Run 배포
# ------------------------------------------------------------------------------
echo "[6/6] 프론트엔드 빌드 및 Google Cloud Run 배포 시작..."
cd "$ROOT_DIR/web"
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build

cd "$ROOT_DIR"
echo "Cloud Run 서비스 배포 중 ($SERVICE_NAME)..."
gcloud run deploy "$SERVICE_NAME" \
    --source="." \
    --platform=managed \
    --region="$SERVICE_REGION" \
    --project="$PROJECT_ID" \
    --service-account="$SA_EMAIL" \
    --allow-unauthenticated \
    --cpu=2 \
    --memory=2Gi \
    --min-instances=1 \
    --max-instances=10 \
    --concurrency=80 \
    --timeout=60m \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${GCP_LOCATION},DEFAULT_APP_ID=${APP_ID},DEFAULT_DEPLOYMENT_ID=${DEPLOYMENT_ID},LOG_LEVEL=INFO,MOCK_MODE=false,JWT_SECRET_KEY=${JWT_SECRET}"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$SERVICE_REGION" --project="$PROJECT_ID" --format="value(status.url)")

echo ""
echo "================================================================="
echo "배포가 성공적으로 완료되었습니다."
echo "웹 콘솔 URL:   $SERVICE_URL"
echo "서비스 헬스체크: $SERVICE_URL/health"
echo "================================================================="
