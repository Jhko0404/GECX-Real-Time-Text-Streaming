"""JWT Ephemeral Ticket Authentication Service."""

import time
import logging
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from .config import settings

logger = logging.getLogger(__name__)

def create_session_ticket(client_id: str, session_id: str, app_id: Optional[str] = None) -> str:
    """Generate a short-lived (60s TTL) signed JWT ticket for streaming connection."""
    now = int(time.time())
    payload = {
        "sub": client_id,
        "session_id": session_id,
        "app_id": app_id or settings.DEFAULT_APP_ID,
        "iat": now,
        "exp": now + settings.JWT_EXPIRATION_SECONDS
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def verify_session_ticket(token: str) -> Optional[Dict[str, Any]]:
    """Validate JWT ticket signature and expiration."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT ticket verification failed: {e}")
        return None
