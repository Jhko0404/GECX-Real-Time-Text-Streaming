"""Pydantic data models for request, response, and SSE streaming events."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SessionStartRequest(BaseModel):
    client_id: str = Field(default="web-cockpit-user", description="Client identifier")
    app_id: Optional[str] = Field(default=None, description="Target CXAS App ID")
    session_id: Optional[str] = Field(default=None, description="Custom Session ID")

class SessionStartResponse(BaseModel):
    session_id: str
    ticket: str
    expires_in: int = 60
    app_id: str
    sse_endpoint: str = "/api/v1/chat/stream"
    ws_endpoint: str = "/ws/chat"
    available_agents: Dict[str, Any]

class ChatStreamRequest(BaseModel):
    session_id: str
    message: str
    app_id: Optional[str] = None
    deployment_id: Optional[str] = None

class ToolCallPayload(BaseModel):
    call_id: str
    tool_name: str
    args: Dict[str, Any] = Field(default_factory=dict)
    status: str = "executing"

class ToolResponsePayload(BaseModel):
    call_id: str
    tool_name: str
    result: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0

class StreamTelemetry(BaseModel):
    ttft_ms: float
    tps: float
    total_tokens: int
    total_latency_ms: float
    model: str = "gemini-3.7-flash"

class SSEEventData(BaseModel):
    event: str  # start, text_chunk, tool_call, tool_response, telemetry, end, error
    data: Dict[str, Any]
