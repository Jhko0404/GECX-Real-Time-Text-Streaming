"""Configuration loader and GCP resource path builder."""

import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # GCP Project & Location
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "gemeni-workshop")
    GCP_PROJECT_NUMBER: str = os.getenv("GCP_PROJECT_NUMBER", "329992103474")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us")
    SERVICE_REGION: str = os.getenv("SERVICE_REGION", "us-central1")

    # Primary Agent: Pre-routing Test Agent
    DEFAULT_APP_ID: str = os.getenv("DEFAULT_APP_ID", "8f0230a9-836f-4795-b57a-0f604540b614")
    DEFAULT_APP_NAME: str = os.getenv("DEFAULT_APP_NAME", "pre_routing_test_agent")
    DEFAULT_DEPLOYMENT_ID: str = os.getenv("DEFAULT_DEPLOYMENT_ID", "0b7d820b-375b-4333-b2ed-474eb0b070a9")

    # Server & Security
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "gecx-text-streaming-secret-key-change-in-prod")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_SECONDS: int = int(os.getenv("JWT_EXPIRATION_SECONDS", "60"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Mock Mode for offline testing
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes")

    def get_app_resource_path(self, app_id: Optional[str] = None) -> str:
        target_app = app_id if app_id else self.DEFAULT_APP_ID
        return f"projects/{self.GCP_PROJECT_ID}/locations/{self.GCP_LOCATION}/apps/{target_app}"

    def get_session_path(self, session_id: str, app_id: Optional[str] = None) -> str:
        app_path = self.get_app_resource_path(app_id)
        return f"{app_path}/sessions/{session_id}"

    def get_default_deployment_path(self, app_id: Optional[str] = None) -> str:
        target_app = app_id if app_id else self.DEFAULT_APP_ID
        return f"projects/{self.GCP_PROJECT_ID}/locations/{self.GCP_LOCATION}/apps/{target_app}/deployments/{self.DEFAULT_DEPLOYMENT_ID}"

    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        return {
            self.DEFAULT_APP_ID: {
                "id": self.DEFAULT_APP_ID,
                "name": self.DEFAULT_APP_NAME,
                "displayName": "사전 라우팅 & 인사 상담원 (pre_routing_test_agent)",
                "description": "Greeting 도구 및 상담사 연결 라우팅 검증 봇",
                "deploymentId": self.DEFAULT_DEPLOYMENT_ID,
                "isDefault": True
            }
        }

settings = Settings()
