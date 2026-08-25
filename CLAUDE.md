# 🤖 Coway GECX Real-Time Text Streaming - Claude Code Guide

> **This document is written for Claude Code CLI to assist engineers in understanding, configuring, testing, and deploying the Coway GECX Text Streaming solution to Google Cloud Platform.**

---

## 📌 Project Overview
* **Name**: `coway-gecx-text-streaming`
* **Architecture**: Hybrid Server-Sent Events (SSE) Backend-For-Frontend (BFF) built with **FastAPI** + **React 18** (Vite + TailwindCSS).
* **AI Engine**: Google Cloud Customer Engagement Suite (CES / GECX) with **Gemini 3.7 Flash**.
* **Key Features**:
  * Ultra-low latency token streaming (TTFT < 450ms, TPS > 120 tokens/sec).
  * Real-time Tool Call Inspector (Args & Results visualization).
  * Authenticated GCS Image Proxy for private manual/diagram images.
  * 60s short-lived signed JWT session tickets.

---

## ⚡ Essential Commands Cheat Sheet

### 1. Initial Setup & Prerequisites
```bash
# Setup Python virtualenv and install Node dependencies + build frontend
./scripts/setup_env.sh
```

### 2. Interactive Customer Deployment Wizard (Recommended)
```bash
# Collects customer GCP environment settings and deploys everything automatically
./scripts/customer_wizard_deploy.sh
```

### 3. Local Development Run
```bash
# Offline Mock Mode (No GCP credentials needed)
./scripts/run_local.sh --mock

# Live GECX Connected Mode
./scripts/run_local.sh
# Open in browser: http://localhost:8080
```

### 4. Run Automated Test Suite (20 Comprehensive Test Cases)
```bash
.venv/bin/python -m unittest discover tests -v
```

### 5. Direct Cloud Run Deployment
```bash
# Deploy to Google Cloud Run with existing .env
./scripts/deploy_cloudrun.sh <GCP_PROJECT_ID>
```

---

## 🔑 Environment Variables (`.env`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | Customer GCP Project ID | `gemeni-workshop` |
| `GCP_LOCATION` | GECX Region (`us` or `global`) | `us` |
| `SERVICE_REGION` | Cloud Run Deployment Region | `us-central1` |
| `DEFAULT_APP_ID` | CX Agent Studio App UUID | `8f0230a9-836f-4795-b57a-0f604540b614` |
| `DEFAULT_DEPLOYMENT_ID` | App Deployment ID | `0b7d820b-375b-4333-b2ed-474eb0b070a9` |
| `DEFAULT_APP_NAME` | Agent Display Name | `pre_routing_test_agent` |
| `JWT_SECRET_KEY` | Secret for short-lived tickets | `coway-gecx-prod-secret-key` |
| `MOCK_MODE` | Enable offline mock simulation | `false` |

---

## 🛡️ Required GCP IAM Roles

The Cloud Run Service Account (`coway-gecx-bff-sa@<PROJECT_ID>.iam.gserviceaccount.com`) requires:
1. `roles/ces.client` (Invoke GECX `runSession` inference)
2. `roles/storage.objectViewer` (Read private manual diagrams from GCS bucket)
3. `roles/logging.logWriter` (Write Cloud Logging entries)

---

## 📁 Repository Directory Structure

```text
coway-gecx-text-streaming/
├── bff/                     # FastAPI Backend-For-Frontend
│   ├── main.py              # Entry point & REST/SSE/Image-Proxy routes
│   ├── gecx_text_client.py  # Google CES runSession HTTP/2 Streaming Client
│   ├── auth.py              # Ephemeral JWT Ticket Manager
│   ├── sse_manager.py       # text/event-stream Serializer
│   └── telemetry.py         # TTFT & TPS Benchmarker
├── web/                     # React 18 + TailwindCSS Frontend Cockpit
│   ├── src/components/      # ChatWindow (Markdown + Lightbox), ToolInspector, TelemetryStrip
│   └── src/engine/          # AdaptiveTypewriterEngine (Paced Token Stream)
├── tests/                   # 20 Comprehensive Unit/Integration Test Cases
├── scripts/                 # Setup, Wizard Deploy, Run scripts
├── docs/                    # Architecture (sdd.md, tdd.md) & Customer Guide
├── CLAUDE.md                # Claude Code Instruction Guide
└── Dockerfile               # Production Multi-Stage Container Spec
```
