# 📘 Coway GECX Real-Time Text Streaming - 고객사 엔지니어 배포 가이드

본 문서는 **Google Cloud Customer Engagement Suite (CES / GECX)** 기반의 **실시간 텍스트 스트리밍 웹 콕핏 솔루션**을 고객사 GCP 프로젝트 환경에 안전하고 신속하게 배포하기 위한 마스터 엔지니어링 가이드입니다.

---

## 📋 1. 사전 준비사항 (Prerequisites)

배포를 진행하기 전에 고객사 터미널에 아래 도구가 설치되어 있어야 합니다.

1. **Google Cloud SDK (`gcloud` CLI)**:
   ```bash
   # gcloud 설치 확인
   gcloud version
   ```
2. **Node.js (v18 이상) & npm**:
   ```bash
   node -v
   npm -v
   ```
3. **Python (3.10 이상)**:
   ```bash
   python3 --version
   ```
4. **Claude Code CLI (선택사항 - Claude Code 사용 고객)**:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

---

## 🔑 2. Google Cloud 인증 및 로그인

GCP 리소스에 접근하고 Cloud Run을 배포하기 위해 고객사 GCP 계정으로 로그인합니다.

```bash
# 1) gcloud CLI 사용자 인증
gcloud auth login

# 2) 애플리케이션 기본 자격증명(ADC) 토큰 발급 (GECX runSession 및 로컬 테스트 필수)
gcloud auth application-default login

# 3) 현재 활성 계정 및 기본 프로젝트 확인
gcloud auth list
gcloud config set project <고객사_GCP_PROJECT_ID>
```

---

## 🚀 3. 초간편 배포 방법 (3가지 옵션)

### 💡 옵션 A: Claude Code를 사용하는 경우 (가장 권장 ⭐)

고객사에서 **클로드 코드 (Claude Code)**를 사용하시는 경우, 프로젝트 루트에서 `claude`를 실행하고 한 줄만 입력하면 됩니다.

```bash
cd coway-gecx-text-streaming
claude
```

> **Claude Code에게 보낼 프롬프트:**
> ```text
> 우리 GCP 환경(Project ID: <고객사_PROJECT_ID>, App ID: <고객사_APP_ID>, Deployment ID: <고객사_DEPLOYMENT_ID>)에 맞게 GECX 텍스트 스트리밍 서비스를 배포해줘.
> ```
> *(Claude Code가 `CLAUDE.md`를 읽고 의존성 설치, 환경변수 구성, IAM 권한 부여, Cloud Run 배포까지 전자동으로 수행합니다.)*

---

### 💡 옵션 B: 대화형 원클릭 마법사 스크립트 실행

별도의 프롬프트 없이 대화형 쉘 스크립트로 배포하려면 아래 스크립트를 실행합니다.

```bash
cd coway-gecx-text-streaming
./scripts/customer_wizard_deploy.sh
```

**마법사 진행 단계:**
1. GCP Project ID 입력
2. GECX Location (`us`) 및 Cloud Run Region (`us-central1`) 확인
3. CX Agent Studio App ID 및 Deployment ID 입력
4. 필수 GCP API 자동 활성화
5. 전용 서비스 계정(`coway-gecx-bff-sa`) 생성 및 IAM 권한 자동 부여
6. 프론트엔드 빌드 & Cloud Run 배포 완료 후 **Live URL 자동 출력**

---

### 💡 옵션 C: 수동 단계별 배포 (Manual Step-by-Step)

#### 1) 환경 설정 파일(`.env`) 생성
```bash
cp .env.example .env
# .env 파일을 열어 고객사 GCP_PROJECT_ID, DEFAULT_APP_ID, DEFAULT_DEPLOYMENT_ID를 입력합니다.
```

#### 2) 필수 API 활성화 및 IAM 권한 설정
```bash
PROJECT_ID="<고객사_GCP_PROJECT_ID>"
SA_NAME="coway-gecx-bff-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# API 활성화
gcloud services enable run.googleapis.com ces.googleapis.com storage.googleapis.com cloudbuild.googleapis.com --project="$PROJECT_ID"

# 서비스 계정 생성
gcloud iam service-accounts create "$SA_NAME" --display-name="Coway GECX BFF" --project="$PROJECT_ID"

# 권한 부여
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_EMAIL}" --role="roles/ces.client"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectViewer"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_EMAIL}" --role="roles/logging.logWriter"
```

#### 3) 프론트엔드 빌드 & Cloud Run 배포
```bash
# Frontend Build
cd web && npm install && npm run build && cd ..

# Cloud Run Deploy
./scripts/deploy_cloudrun.sh "$PROJECT_ID"
```

---

## 🧪 4. 배포 후 자동 검증 (20개 테스트 스위트)

배포 전후로 로컬에서 20개 핵심 기능(JWT 보안, SSE 스트리밍, 텔레메트리 연산, GCS 이미지 프록시)을 자동 테스트할 수 있습니다.

```bash
# 가상환경 구성
./scripts/setup_env.sh

# 20개 테스트 일괄 실행
.venv/bin/python -m unittest discover tests -v
```

---

## 🔍 5. 문제 해결 (Troubleshooting)

### Q1. "Anonymous caller does not have storage.objects.get access" 에러 발생 시
* **원인**: GCS 비공개 다이어그램 이미지 버킷 접근 시 브라우저가 직접 접근하려 할 때 발생.
* **해결**: 본 솔루션에 내장된 **BFF Image Proxy (`/api/v1/image-proxy?url=...`)**가 자동으로 중계하며, Cloud Run 서비스 계정에 `roles/storage.objectViewer` 권한이 부여되어 있는지 확인합니다.

### Q2. 텍스트 스트리밍 중 401 Unauthorized 에러 발생 시
* **원인**: 단기 세션 티켓(60s TTL)이 만료되었거나 서명 불일치.
* **해결**: 웹 콘솔 우측 상단의 **[세션 초기화(새로고침)]** 버튼을 클릭하여 새 티켓을 발급받습니다.
