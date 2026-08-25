"""Server-Sent Events (SSE) Stream Manager."""

import json
from typing import AsyncGenerator, Dict, Any

async def format_sse_stream(event_generator: AsyncGenerator[Dict[str, Any], None]) -> AsyncGenerator[str, None]:
    """Format raw event dictionaries into SSE text/event-stream standard format."""
    try:
        async for event in event_generator:
            event_type = event.get("event", "message")
            event_data = json.dumps(event.get("data", {}), ensure_ascii=False)
            yield f"event: {event_type}\ndata: {event_data}\n\n"
    except Exception as e:
        error_payload = json.dumps({"error": str(e)}, ensure_ascii=False)
        yield f"event: error\ndata: {error_payload}\n\n"
