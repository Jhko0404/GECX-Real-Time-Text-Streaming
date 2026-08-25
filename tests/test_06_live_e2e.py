"""Section 6: Live GECX & Cloud Run E2E Integration (TC-18 ~ TC-20)."""

import unittest
import asyncio
from bff.config import settings
from bff.gecx_text_client import GECXTextClient

class TestSection06LiveE2E(unittest.TestCase):
    def setUp(self):
        settings.MOCK_MODE = False
        self.client = GECXTextClient()

    def test_tc18_live_gecx_credentials_and_token(self):
        """TC-18: Verify Google ADC credential resolution and Bearer token acquisition."""
        token = self.client._get_access_token()
        self.assertIsNotNone(token)
        self.assertTrue(len(token) > 20)

    def test_tc19_live_gecx_greeting_stream_turn(self):
        """TC-19: Live GECX greeting stream turn with greeting Tool Call and text output."""
        import uuid
        sess_id = f"test_e2e_tc19_{uuid.uuid4().hex[:6]}"
        async def run_live():
            events = []
            async for ev in self.client.stream_turn(sess_id, "안녕하세요"):
                events.append(ev)
            return events

        events = asyncio.run(run_live())
        event_types = [e["event"] for e in events]
        
        self.assertIn("start", event_types)
        self.assertIn("text_chunk", event_types)
        self.assertIn("telemetry", event_types)
        self.assertIn("end", event_types)

        # Verify text chunk content
        text_chunks = [e["data"]["delta"] for e in events if e["event"] == "text_chunk"]
        full_text = "".join(text_chunks)
        self.assertTrue("안녕하세요" in full_text or "고객님" in full_text)

    def test_tc20_live_gecx_multi_turn_telemetry_benchmark(self):
        """TC-20: Live GECX multi-turn stream with microsecond TTFT & TPS metrics."""
        import uuid
        sess_id = f"test_e2e_tc20_{uuid.uuid4().hex[:6]}"
        async def run_multi_turn():
            turn1 = [e async for e in self.client.stream_turn(sess_id, "안녕하세요")]
            turn2 = [e async for e in self.client.stream_turn(sess_id, "이름이 무엇인가요?")]
            return turn1, turn2

        t1, t2 = asyncio.run(run_multi_turn())
        
        # Check telemetry in turn 1
        telemetry_ev = next((e for e in t1 if e["event"] == "telemetry"), None)
        self.assertIsNotNone(telemetry_ev)
        t_data = telemetry_ev["data"]
        self.assertGreater(t_data["ttft_ms"], 0)
        self.assertGreater(t_data["tps"], 0)
        self.assertGreater(t_data["total_tokens"], 0)

        # Check turn 2 completed
        self.assertTrue(any(e["event"] == "end" for e in t2))

if __name__ == "__main__":
    unittest.main()
