"""Section 1: Security & Ephemeral JWT Ticket Tests (TC-01 ~ TC-04)."""

import unittest
import time
from jose import jwt
from bff.auth import create_session_ticket, verify_session_ticket
from bff.config import settings

class TestSection01SecurityAuth(unittest.TestCase):
    def test_tc01_valid_ticket_creation_and_verification(self):
        """TC-01: 60s TTL JWT ticket generation and signature verification."""
        client_id = "cockpit-tester-01"
        session_id = "sess-sec-test-01"
        token = create_session_ticket(client_id, session_id)
        
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        
        payload = verify_session_ticket(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], client_id)
        self.assertEqual(payload["session_id"], session_id)
        self.assertEqual(payload["app_id"], settings.DEFAULT_APP_ID)
        self.assertGreater(payload["exp"], payload["iat"])

    def test_tc02_expired_ticket_rejection(self):
        """TC-02: Expired JWT ticket rejection test."""
        now = int(time.time())
        expired_payload = {
            "sub": "user-expired",
            "session_id": "sess-expired",
            "app_id": settings.DEFAULT_APP_ID,
            "iat": now - 120,
            "exp": now - 60  # Expired 60s ago
        }
        expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        verified = verify_session_ticket(expired_token)
        self.assertIsNone(verified, "Expired ticket must be rejected")

    def test_tc03_tampered_signature_detection(self):
        """TC-03: Tampered JWT signature detection and rejection."""
        token = create_session_ticket("legit-user", "sess-legit")
        tampered_token = token[:-6] + "BADSIG"
        verified = verify_session_ticket(tampered_token)
        self.assertIsNone(verified, "Tampered signature must be rejected")

    def test_tc04_empty_and_malformed_token_rejection(self):
        """TC-04: Empty and malformed token rejection."""
        self.assertIsNone(verify_session_ticket(""))
        self.assertIsNone(verify_session_ticket("not.a.valid.jwt.token.structure"))
        self.assertIsNone(verify_session_ticket("Bearer 12345"))

if __name__ == "__main__":
    unittest.main()
