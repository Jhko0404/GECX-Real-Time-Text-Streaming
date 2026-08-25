"""Section 4: SSE Stream Serialization & Framing (TC-11 ~ TC-14)."""

import unittest
import json
from bff.sse_manager import format_sse_stream

class TestSection04SSESerialization(unittest.TestCase):
    async def _collect_sse_output(self, generator):
        output = []
        async for line in format_sse_stream(generator):
            output.append(line)
        return "".join(output)

    def test_tc11_event_start_serialization(self):
        """TC-11: event: start serialization."""
        import asyncio
        async def sample_gen():
            yield {"event": "start", "data": {"session_id": "s1", "app_id": "a1"}}

        result = asyncio.run(self._collect_sse_output(sample_gen()))
        self.assertIn("event: start\n", result)
        self.assertIn('"session_id": "s1"', result)
        self.assertTrue(result.endswith("\n\n"))

    def test_tc12_event_tool_call_and_response_serialization(self):
        """TC-12: event: tool_call and tool_response JSON framing."""
        import asyncio
        async def sample_gen():
            yield {
                "event": "tool_call",
                "data": {"call_id": "c1", "tool_name": "greeting", "args": {}}
            }
            yield {
                "event": "tool_response",
                "data": {"call_id": "c1", "tool_name": "greeting", "result": {"msg": "hi"}}
            }

        result = asyncio.run(self._collect_sse_output(sample_gen()))
        self.assertIn("event: tool_call\n", result)
        self.assertIn("event: tool_response\n", result)
        self.assertIn('"greeting"', result)

    def test_tc13_event_text_chunk_sequence_framing(self):
        """TC-13: event: text_chunk delta and sequence numbering."""
        import asyncio
        async def sample_gen():
            yield {"event": "text_chunk", "data": {"delta": "안녕", "sequence": 1}}
            yield {"event": "text_chunk", "data": {"delta": "하세요", "sequence": 2}}

        result = asyncio.run(self._collect_sse_output(sample_gen()))
        self.assertIn('"delta": "안녕"', result)
        self.assertIn('"sequence": 1', result)
        self.assertIn('"delta": "하세요"', result)
        self.assertIn('"sequence": 2', result)

    def test_tc14_event_telemetry_and_end_framing(self):
        """TC-14: event: telemetry and event: end STOP signal."""
        import asyncio
        async def sample_gen():
            yield {"event": "telemetry", "data": {"ttft_ms": 320.5, "tps": 45.0, "total_tokens": 10, "total_latency_ms": 500.0, "model": "gemini-3.7-flash"}}
            yield {"event": "end", "data": {"finish_reason": "STOP"}}

        result = asyncio.run(self._collect_sse_output(sample_gen()))
        self.assertIn("event: telemetry\n", result)
        self.assertIn("event: end\n", result)
        self.assertIn('"finish_reason": "STOP"', result)

if __name__ == "__main__":
    unittest.main()
