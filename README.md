# 💬 Coway GECX Real-Time Text Streaming & Cockpit Console

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Customer Engagement Suite](https://img.shields.io/badge/Google%20Cloud-CX%20Agent%20Studio-34A853?logo=google&logoColor=white)](https://cloud.google.com/customer-engagement-ai/conversational-agents/ps)
[![Gemini](https://img.shields.io/badge/Model-Gemini%203.7%20Flash-8E75B2?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

> **Google Cloud Customer Engagement Suite (CES / GECX)의 `Gemini 3.7 Flash` 모델을 기반으로 하는 실시간 텍스트 토큰 스트리밍(SSE) 및 코웨이 공식 브랜드 웹 콕핏 콘솔 솔루션입니다.**

---

## 🌟 핵심 기능 (Highlights)

* **초저지연 텍스트 토큰 스트리밍 (SSE)**:
  * HTTP/2 기반 **Server-Sent Events (`text/event-stream`)**로 단어/글자 생성 즉시 실시간 타자기 렌더링.
  * **Hyper-TTFT 최적화**: 커넥션 풀링 + 0ms 첫 청크 즉시 바이패스로 TTFT 대폭 단축.
* **실시간 도구 호출 인스펙터 (Tool Call Inspector)**:
  * 에이전트가 실행한 Python 툴(`greeting`, 상담사 연결 사전 라우팅 등)의 인자(Args)와 반환값(Result)을 실시간 JSON 트리로 시각화.
* **보안 이미지 프록시 (GCS Authenticated Image Proxy)**:
  * 비공개 GCS 버킷에 저장된 정수기/공기청정기 매뉴얼 및 필터 다이어그램 이미지를 Signed URL 없이 서비스 계정 IAM 권한으로 안전하고 빠르게 중계 렌더링.
* **클릭 확대 뷰어 (Lightbox Modal)**:
  * 다이어그램/필터 설명 이미지를 클릭하면 전체 화면 고해상도 확대 모달 표출.
* **코웨이 공식 브랜드 테마**:
  * 퓨어 화이트 & 스노우 그레이 배경 (`#f4f7fb`) + 코웨이 시그니처 아이스 블루 (`#0080ff`).

---

## ⚡ 빠른 시작 & 고객사 배포 (Quick Start)

### 🤖 1. Claude Code로 원클릭 배포 (가장 권장)
고객사에서 **Claude Code**를 사용하시는 경우, 아래 명령어를 실행하면 `CLAUDE.md` 지침에 따라 전자동으로 배포됩니다:

```bash
cd coway-gecx-text-streaming
claude
```
> **Claude 프롬프트:** *"우리 GCP 환경에 맞게 GECX 텍스트 스트리밍 서비스를 배포해줘."*

---

### 🧙‍♂️ 2. 대화형 마법사 스크립트로 배포
```bash
cd coway-gecx-text-streaming
./scripts/customer_wizard_deploy.sh
```

---

### 💻 3. 로컬 테스트 실행
```bash
# 환경 설정
./scripts/setup_env.sh

# Mock 모드 (GCP 연결 없이 오프라인 테스트)
./scripts/run_local.sh --mock

# Live GECX 모드 (실제 GCP 에이전트와 실시간 대화)
./scripts/run_local.sh
# 👉 브라우저 접속: http://localhost:8080
```

---

### 🧪 4. 20개 단위 및 통합 테스트 실행
```bash
.venv/bin/python -m unittest discover tests -v
```

---

## 📚 기술 문서 색인 (Documentation)

* 📘 [고객사 엔지니어 배포 가이드 (CUSTOMER_DEPLOYMENT_GUIDE.md)](docs/CUSTOMER_DEPLOYMENT_GUIDE.md) - GCP 콘솔 로그인부터 시작하는 A to Z 가이드
* 📐 [기술 상세 설계서 (TDD)](docs/tdd.md) - 적응형 타자기 알고리즘, Pydantic 스키마, 텔레메트리 연산 설계
* 📘 [솔루션 마스터 설계서 (SDD)](docs/sdd.md) - 전체 아키텍처 및 IAM 보안 설계
* 🧪 [종합 테스트 결과 보고서 (TEST_REPORT.md)](docs/TEST_REPORT.md) - 20개 테스트 케이스 전수 검증 결과
* 🤖 [Claude Code 인스트럭션 가이드 (CLAUDE.md)](CLAUDE.md) - Claude Code CLI 전용 가이드
