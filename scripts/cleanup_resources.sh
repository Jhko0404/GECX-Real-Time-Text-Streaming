#!/bin/bash
set -e

# ==============================================================================
# GECX Real-Time Text Streaming - Resource Cleanup Script
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

echo "================================================================="
echo "[GECX] 배포 리소스 정리 및 삭제 (Resource Cleanup)"
echo "================================================================="
echo "본 스크립트는 GECX-Real-Time-Text-Streaming 솔루션을 위해 생성된"
echo "Cloud Run 서비스 및 전용 서비스 계정(IAM)만 안전하게 삭제합니다."
echo "================================================================="
echo ""

# ------------------------------------------------------------------------------
# 1단계: .env 또는 gcloud에서 대상 환경값 로드
# ------------------------------------------------------------------------------
if [ -f .env ]; then
    PROJECT_ID=$(grep '^GCP_PROJECT_ID=' .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    SERVICE_REGION=$(grep '^SERVICE_REGION=' .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
fi

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
SERVICE_REGION="${SERVICE_REGION:-us-central1}"
SERVICE_NAME="GECX-Real-Time-Text-Streaming"
SA_NAME="gecx-bff-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# ------------------------------------------------------------------------------
# 2단계: 배포된 리소스 식별 및 상태 점검 (더블 체크 1)
# ------------------------------------------------------------------------------
echo "[1/3] 대상 프로젝트 및 리소스 존재 여부 확인 중..."
echo "  - 대상 GCP Project ID: $PROJECT_ID"
echo "  - 대상 Region:         $SERVICE_REGION"
echo ""

SERVICE_EXISTS=false
SA_EXISTS=false

if gcloud run services describe "$SERVICE_NAME" --region="$SERVICE_REGION" --project="$PROJECT_ID" &>/dev/null; then
    SERVICE_EXISTS=true
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$SERVICE_REGION" --project="$PROJECT_ID" --format="value(status.url)")
    echo "  [발견] Cloud Run 서비스: $SERVICE_NAME ($SERVICE_URL)"
else
    echo "  [미발견] Cloud Run 서비스: $SERVICE_NAME (이미 삭제되었거나 배포되지 않음)"
fi

if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    SA_EXISTS=true
    echo "  [발견] 서비스 계정:       $SA_EMAIL"
else
    echo "  [미발견] 서비스 계정:       $SA_EMAIL (이미 삭제되었거나 생성되지 않음)"
fi
echo ""

if [ "$SERVICE_EXISTS" = false ] && [ "$SA_EXISTS" = false ]; then
    echo "삭제할 GECX-Real-Time-Text-Streaming 리소스가 존재하지 않습니다. 종료합니다."
    exit 0
fi

# ------------------------------------------------------------------------------
# 3단계: 안전 더블 체크 (Double Check Confirmation)
# ------------------------------------------------------------------------------
echo "-----------------------------------------------------------------"
echo "[주의] 아래 리소스가 영구적으로 삭제됩니다:"
if [ "$SERVICE_EXISTS" = true ]; then
    echo "  1) Cloud Run Service:  $SERVICE_NAME (Region: $SERVICE_REGION)"
fi
if [ "$SA_EXISTS" = true ]; then
    echo "  2) Service Account:    $SA_EMAIL"
    echo "  3) IAM Policy Bindings: roles/ces.client, roles/storage.objectViewer, roles/logging.logWriter"
fi
echo "-----------------------------------------------------------------"
echo "※ 다른 서비스나 데이터(GCS 버킷 등)는 삭제되지 않으며 본 솔루션 전용 리소스만 삭제됩니다."
echo ""

read -p "삭제를 진행하려면 프로젝트 ID [$PROJECT_ID]를 정확히 입력하세요: " CONFIRM_INPUT

if [ "$CONFIRM_INPUT" != "$PROJECT_ID" ]; then
    echo "입력값이 일치하지 않습니다. 리소스 삭제가 안전하게 취소되었습니다."
    exit 1
fi
echo ""

# ------------------------------------------------------------------------------
# 4단계: 리소스 순차 삭제
# ------------------------------------------------------------------------------
echo "[2/3] 리소스 삭제 진행 중..."

# 1) Cloud Run 서비스 삭제
if [ "$SERVICE_EXISTS" = true ]; then
    echo "  - Cloud Run 서비스 삭제 중 ($SERVICE_NAME)..."
    gcloud run services delete "$SERVICE_NAME" \
        --region="$SERVICE_REGION" \
        --project="$PROJECT_ID" \
        --quiet
    echo "    Cloud Run 서비스 삭제 완료."
fi

# 2) IAM 역할 바인딩 해제 및 서비스 계정 삭제
if [ "$SA_EXISTS" = true ]; then
    echo "  - IAM 역할 바인딩 제거 중..."
    for ROLE in "roles/ces.client" "roles/storage.objectViewer" "roles/logging.logWriter"; do
        gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:${SA_EMAIL}" \
            --role="$ROLE" \
            --condition=None --quiet >/dev/null 2>&1 || true
    done

    echo "  - 서비스 계정 삭제 중 ($SA_EMAIL)..."
    gcloud iam service-accounts delete "$SA_EMAIL" \
        --project="$PROJECT_ID" \
        --quiet
    echo "    서비스 계정 삭제 완료."
fi

echo ""
echo "================================================================="
echo "[3/3] GECX-Real-Time-Text-Streaming 리소스 삭제가 완료되었습니다."
echo "================================================================="
