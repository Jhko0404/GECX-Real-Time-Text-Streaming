"""Section 2: Configuration & GCP Resource Path Builders (TC-05 ~ TC-07)."""

import unittest
from bff.config import settings

class TestSection02ConfigPaths(unittest.TestCase):
    def test_tc05_app_resource_path_builder(self):
        """TC-05: App resource path builder formatting."""
        path = settings.get_app_resource_path()
        self.assertEqual(
            path,
            f"projects/{settings.GCP_PROJECT_ID}/locations/{settings.GCP_LOCATION}/apps/{settings.DEFAULT_APP_ID}"
        )
        custom_path = settings.get_app_resource_path("custom-app-123")
        self.assertEqual(
            custom_path,
            f"projects/{settings.GCP_PROJECT_ID}/locations/{settings.GCP_LOCATION}/apps/custom-app-123"
        )

    def test_tc06_deployment_resource_path_builder(self):
        """TC-06: Deployment resource path builder formatting."""
        dep_path = settings.get_default_deployment_path()
        self.assertEqual(
            dep_path,
            f"projects/{settings.GCP_PROJECT_ID}/locations/{settings.GCP_LOCATION}/apps/{settings.DEFAULT_APP_ID}/deployments/{settings.DEFAULT_DEPLOYMENT_ID}"
        )

    def test_tc07_session_resource_path_builder(self):
        """TC-07: Session resource path builder formatting."""
        session_id = "test-session-uuid-999"
        sess_path = settings.get_session_path(session_id)
        self.assertEqual(
            sess_path,
            f"projects/{settings.GCP_PROJECT_ID}/locations/{settings.GCP_LOCATION}/apps/{settings.DEFAULT_APP_ID}/sessions/{session_id}"
        )

if __name__ == "__main__":
    unittest.main()
