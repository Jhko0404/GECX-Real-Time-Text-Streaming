"""Section 5: FastAPI REST Endpoints & SSE Streaming (TC-15 ~ TC-17)."""

import unittest
from fastapi.testclient import TestClient
from bff.main import app
from bff.config import settings

class TestSection05APIEndpoints(unittest.TestCase):
    def setUp(self):
        settings.MOCK_MODE = True
        self.client = TestClient(app)

    def test_tc15_health_check_endpoint(self):
        """TC-15: GET /health returns HTTP 200 and healthy status."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "gecx-text-streaming-bff")

    def test_tc16_session_start_control_plane(self):
        """TC-16: POST /api/v1/session/start issues signed short-lived ticket."""
        res = self.client.post("/api/v1/session/start", json={"client_id": "e2e-user"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("session_id", data)
        self.assertIn("ticket", data)
        self.assertEqual(data["expires_in"], 60)
        self.assertIn("available_agents", data)

    def test_tc17_chat_stream_mock_e2e(self):
        """TC-17: POST /api/v1/chat/stream returns valid text/event-stream."""
        start_res = self.client.post("/api/v1/session/start", json={"client_id": "tester"})
        session_id = start_res.json()["session_id"]
        ticket = start_res.json()["ticket"]

        with self.client.stream(
            "POST",
            "/api/v1/chat/stream",
            json={"session_id": session_id, "message": "안녕하세요"},
            headers={"Authorization": f"Bearer {ticket}"}
        ) as res:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers["content-type"], "text/event-stream; charset=utf-8")
            
            chunks = [line for line in res.iter_lines() if line]
            self.assertTrue(any("event: start" in c for c in chunks))
            self.assertTrue(any("event: tool_call" in c for c in chunks))
            self.assertTrue(any("event: tool_response" in c for c in chunks))
            self.assertTrue(any("event: text_chunk" in c for c in chunks))
            self.assertTrue(any("event: telemetry" in c for c in chunks))
            self.assertTrue(any("event: end" in c for c in chunks))

if __name__ == "__main__":
    unittest.main()
