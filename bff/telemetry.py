"""Telemetry and Benchmark Calculator for Text Streaming."""

import time
from typing import Dict, Any, Optional

class TelemetryBenchmark:
    def __init__(self):
        self.start_time: float = time.perf_counter()
        self.first_token_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.total_chars: int = 0
        self.total_tokens_estimated: int = 0

    def record_first_token(self):
        if self.first_token_time is None:
            self.first_token_time = time.perf_counter()

    def record_chunk(self, chunk_text: str):
        self.record_first_token()
        self.total_chars += len(chunk_text)

    def finalize(self) -> Dict[str, Any]:
        self.end_time = time.perf_counter()
        total_latency_ms = (self.end_time - self.start_time) * 1000.0

        if self.first_token_time:
            ttft_ms = (self.first_token_time - self.start_time) * 1000.0
            streaming_duration_sec = max(0.001, self.end_time - self.first_token_time)
        else:
            ttft_ms = total_latency_ms
            streaming_duration_sec = max(0.001, total_latency_ms / 1000.0)

        # Estimate tokens (UTF-8 Korean/English average ~3.2 chars per token)
        self.total_tokens_estimated = max(1, int(self.total_chars / 3.2))
        tps = self.total_tokens_estimated / streaming_duration_sec

        return {
            "ttft_ms": round(ttft_ms, 2),
            "tps": round(tps, 1),
            "total_tokens": self.total_tokens_estimated,
            "total_latency_ms": round(total_latency_ms, 2),
            "model": "gemini-3.7-flash"
        }
