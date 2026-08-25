"""GECX Real-Time Text Streaming BFF - FastAPI Entry Point."""

import os
import uuid
import logging
from typing import Optional
from urllib.parse import unquote, urlparse
from fastapi import FastAPI, HTTPException, Header, Query, WebSocket, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
import google.auth
import google.auth.transport.requests

from .config import settings
from .schemas import SessionStartRequest, SessionStartResponse, ChatStreamRequest
from .auth import create_session_ticket, verify_session_ticket
from .gecx_text_client import gecx_client
from .sse_manager import format_sse_stream
from .ws_manager import ws_manager

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GECX Real-Time Text Streaming BFF",
    description="Backend-for-Frontend service for Google Cloud Customer Engagement Suite (CES) Real-Time Text Streaming.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# 1. Health Check
# ------------------------------------------------------------------------------
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "gecx-text-streaming-bff",
        "mock_mode": settings.MOCK_MODE,
        "default_app": settings.DEFAULT_APP_ID
    }

# ------------------------------------------------------------------------------
# 2. Control Plane: Start Session & Issue Ticket
# ------------------------------------------------------------------------------
@app.post("/api/v1/session/start", response_model=SessionStartResponse)
async def start_session(req: SessionStartRequest):
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:12]}"
    app_id = req.app_id or settings.DEFAULT_APP_ID
    ticket = create_session_ticket(req.client_id, session_id, app_id)

    logger.info(f"Session started: session_id={session_id}, app_id={app_id}, client_id={req.client_id}")
    return SessionStartResponse(
        session_id=session_id,
        ticket=ticket,
        expires_in=settings.JWT_EXPIRATION_SECONDS,
        app_id=app_id,
        sse_endpoint="/api/v1/chat/stream",
        ws_endpoint="/ws/chat",
        available_agents=settings.get_available_agents()
    )

# ------------------------------------------------------------------------------
# 3. Data Plane: SSE Chat Stream (POST /api/v1/chat/stream)
# ------------------------------------------------------------------------------
@app.post("/api/v1/chat/stream")
async def chat_stream(
    req: ChatStreamRequest,
    authorization: Optional[str] = Header(None)
):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = verify_session_ticket(token)
        if not payload:
            logger.warning("Invalid or expired session ticket on SSE stream")

    logger.info(f"Initiating SSE text stream: session_id={req.session_id}, message_len={len(req.message)}")
    
    event_gen = gecx_client.stream_turn(
        session_id=req.session_id,
        user_text=req.message,
        app_id=req.app_id,
        deployment_id=req.deployment_id
    )

    return StreamingResponse(
        format_sse_stream(event_gen),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ------------------------------------------------------------------------------
# 4. GCS Authenticated Image Proxy (GET /api/v1/image-proxy)
# ------------------------------------------------------------------------------
@app.get("/api/v1/image-proxy")
async def gcs_image_proxy(url: str = Query(..., description="GCS Object URL to proxy")):
    """Securely proxy private GCS bucket images to client using Service Account credentials."""
    decoded_url = unquote(url)
    
    # Normalize URL format to storage.googleapis.com
    target_url = decoded_url.replace("https://storage.cloud.google.com/", "https://storage.googleapis.com/")
    
    # Extract bucket and object path
    parsed = urlparse(target_url)
    if not (parsed.netloc.endswith("googleapis.com") or parsed.netloc.endswith("google.com")):
        raise HTTPException(status_code=400, detail="Invalid storage domain")

    try:
        # Get ADC Access Token
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        
        headers = {"Authorization": f"Bearer {creds.token}"}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(target_url, headers=headers)
            if resp.status_code != 200:
                logger.error(f"GCS Image Proxy fetch failed: {resp.status_code} for {target_url}")
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch image from storage")

            media_type = resp.headers.get("Content-Type", "image/png")
            return Response(
                content=resp.content,
                media_type=media_type,
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Access-Control-Allow-Origin": "*"
                }
            )
    except Exception as e:
        logger.exception(f"Error in GCS Image Proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------------------
# 5. Data Plane: WebSocket Chat Stream (WSS /ws/chat)
# ------------------------------------------------------------------------------
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket, ticket: str = Query(...)):
    await ws_manager.handle_websocket(websocket, ticket)

# ------------------------------------------------------------------------------
# 6. Static SPA Serving (Frontend Web UI)
# ------------------------------------------------------------------------------
web_dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "dist")

if os.path.exists(web_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(web_dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_target = os.path.join(web_dist_path, full_path)
        if full_path and os.path.exists(file_target) and not os.path.isdir(file_target):
            return FileResponse(file_target)
        return FileResponse(os.path.join(web_dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bff.main:app", host=settings.HOST, port=settings.PORT, reload=True)
