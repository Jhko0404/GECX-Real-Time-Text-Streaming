"""GECX Core API Client for Text Streaming with Hyper TTFT Optimization."""

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Dict, Any, Optional
import httpx
import google.auth
import google.auth.transport.requests
from .config import settings
from .telemetry import TelemetryBenchmark

logger = logging.getLogger(__name__)

class GECXTextClient:
    def __init__(self):
        self.credentials = None
        self.auth_request = None
        self._cached_token = None
        self._token_expiry = 0
        
        # HTTP Client with Persistent Keep-Alive Connection Pool
        self.http_client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100, keepalive_expiry=120.0),
            timeout=httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=5.0)
        )

        if not settings.MOCK_MODE:
            try:
                self.credentials, _ = google.auth.default(
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                self.auth_request = google.auth.transport.requests.Request()
            except Exception as e:
                logger.warning(f"Google ADC initialization warning: {e}")

    def _get_access_token(self) -> str:
        if settings.MOCK_MODE or not self.credentials:
            return "mock-access-token"
        
        now = time.time()
        if self._cached_token and now < self._token_expiry - 60:
            return self._cached_token

        if not self.credentials.valid or not self._cached_token:
            self.credentials.refresh(self.auth_request)
            self._cached_token = self.credentials.token
            self._token_expiry = now + 3500
        return self._cached_token

    async def stream_turn(
        self,
        session_id: str,
        user_text: str,
        app_id: Optional[str] = None,
        deployment_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute text turn against GECX runSession and stream tool calls and tokens."""
        target_app = app_id or settings.DEFAULT_APP_ID
        session_resource_path = settings.get_session_path(session_id, target_app)
        api_url = f"https://ces.googleapis.com/v1beta/{session_resource_path}:runSession"
        benchmark = TelemetryBenchmark()

        # 1. Start event
        yield {
            "event": "start",
            "data": {
                "session_id": session_id,
                "app_id": target_app,
                "timestamp": time.time()
            }
        }

        if settings.MOCK_MODE:
            async for event in self._mock_stream(user_text, benchmark):
                yield event
            return

        # 2. Live Request
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        target_deployment = deployment_id or settings.get_default_deployment_path(target_app)
        config_payload: Dict[str, Any] = {
            "session": session_resource_path,
            "deployment": target_deployment
        }

        body = {
            "config": config_payload,
            "inputs": [{"text": user_text}]
        }

        try:
            response = await self.http_client.post(api_url, headers=headers, json=body)
            
            if response.status_code != 200:
                error_msg = f"GECX API returned HTTP {response.status_code}: {response.text}"
                logger.error(error_msg)
                yield {
                    "event": "error",
                    "data": {"error": error_msg, "status_code": response.status_code}
                }
                return

            res_json = response.json()
            outputs = res_json.get("outputs", [])

            for out in outputs:
                # 1. Parse Tool Calls & Responses from Diagnostic Messages
                diag = out.get("diagnosticInfo", {})
                messages = diag.get("messages", [])
                for msg in messages:
                    if msg.get("role") == "user":
                        continue
                    chunks = msg.get("chunks", [])
                    for sub in chunks:
                        # Tool Call
                        tool_call = sub.get("toolCall")
                        if tool_call:
                            yield {
                                "event": "tool_call",
                                "data": {
                                    "call_id": tool_call.get("id", "call-id"),
                                    "tool_name": tool_call.get("displayName") or tool_call.get("tool", "tool"),
                                    "args": tool_call.get("args", {})
                                }
                            }

                        # Tool Response
                        tool_response = sub.get("toolResponse")
                        if tool_response:
                            yield {
                                "event": "tool_response",
                                "data": {
                                    "call_id": tool_response.get("id", "call-id"),
                                    "tool_name": tool_response.get("displayName") or tool_response.get("tool", "tool"),
                                    "result": tool_response.get("response", {}).get("result", {})
                                }
                            }

                        # Updated Variables
                        updated_vars = sub.get("updatedVariables")
                        if updated_vars:
                            yield {
                                "event": "updated_variables",
                                "data": updated_vars
                            }

                # 2. Parse Final Agent Text Output
                agent_text = out.get("text")
                if agent_text:
                    words = agent_text.split(" ")
                    for idx, word in enumerate(words):
                        token_delta = word + (" " if idx < len(words) - 1 else "")
                        benchmark.record_chunk(token_delta)
                        yield {
                            "event": "text_chunk",
                            "data": {
                                "delta": token_delta,
                                "sequence": idx + 1
                            }
                        }
                        if idx > 0:
                            await asyncio.sleep(0.015) # fast 15ms streaming cadence

            # 3. Telemetry & End
            telemetry_data = benchmark.finalize()
            yield {
                "event": "telemetry",
                "data": telemetry_data
            }
            yield {
                "event": "end",
                "data": {"finish_reason": "STOP"}
            }

        except Exception as e:
            logger.exception(f"Error during GECX streaming: {e}")
            yield {"event": "error", "data": {"error": str(e)}}

    async def _mock_stream(self, user_text: str, benchmark: TelemetryBenchmark) -> AsyncGenerator[Dict[str, Any], None]:
        await asyncio.sleep(0.05)
        yield {
            "event": "tool_call",
            "data": {"call_id": "mock-call", "tool_name": "greeting", "args": {}}
        }
        await asyncio.sleep(0.05)
        yield {
            "event": "tool_response",
            "data": {"call_id": "mock-call", "tool_name": "greeting", "result": {"status": "ok"}}
        }
        mock_reply = f"안녕하세요! 무엇을 도와드릴까요? (질문: {user_text})"
        for idx, word in enumerate(mock_reply.split(" ")):
            delta = word + " "
            benchmark.record_chunk(delta)
            yield {"event": "text_chunk", "data": {"delta": delta, "sequence": idx + 1}}
            await asyncio.sleep(0.015)

        yield {"event": "telemetry", "data": benchmark.finalize()}
        yield {"event": "end", "data": {"finish_reason": "STOP"}}

gecx_client = GECXTextClient()
