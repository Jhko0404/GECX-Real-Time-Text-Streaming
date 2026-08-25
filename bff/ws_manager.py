"""WebSocket Connection & Chat Stream Manager."""

import json
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from .auth import verify_session_ticket
from .gecx_text_client import gecx_client

logger = logging.getLogger(__name__)

class WebSocketChatManager:
    async def handle_websocket(self, websocket: WebSocket, ticket: str):
        # 1. Validate Ticket
        payload = verify_session_ticket(ticket)
        if not payload:
            await websocket.close(code=4401, reason="Invalid or expired session ticket")
            return

        session_id = payload.get("session_id")
        app_id = payload.get("app_id")

        await websocket.accept()
        logger.info(f"WebSocket client connected: session={session_id}, app={app_id}")

        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    msg_json = json.loads(data_text)
                except Exception:
                    msg_json = {"text": data_text}

                user_message = msg_json.get("text") or msg_json.get("message", "")
                override_app = msg_json.get("app_id") or app_id

                if not user_message:
                    continue

                # Stream response events over WebSocket
                async for event in gecx_client.stream_turn(session_id, user_message, override_app):
                    await websocket.send_text(json.dumps(event, ensure_ascii=False))

        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected: session={session_id}")
        except Exception as e:
            logger.error(f"WebSocket exception for session={session_id}: {e}")
            try:
                await websocket.send_text(json.dumps({"event": "error", "data": {"error": str(e)}}))
                await websocket.close(code=1011, reason=str(e))
            except Exception:
                pass

ws_manager = WebSocketChatManager()
