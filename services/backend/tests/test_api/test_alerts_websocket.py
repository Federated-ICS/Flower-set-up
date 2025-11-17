"""
Tests for Alerts API WebSocket Integration
Following TDD approach - RED phase
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestAlertsWebSocketIntegration:
    """Test that Alerts API emits WebSocket events"""

    @pytest.mark.asyncio
    async def test_create_alert_emits_event(self, test_db):
        """Test that creating an alert emits alert_created event"""
        with patch("app.api.alerts.emit_alert_created") as mock_emit:
            mock_emit.return_value = AsyncMock()

            # Create an alert
            response = client.post(
                "/api/alerts",
                json={
                    "title": "Test Alert",
                    "description": "Test Description",
                    "severity": "high",
                    "facility_id": "facility-1",
                    "attack_type": "port_scan",
                    "sources": [
                        {
                            "layer": 1,
                            "model_name": "test_model",
                            "confidence": 0.95,
                            "detection_time": "2025-11-11T12:00:00",
                            "evidence": "Test evidence",
                        }
                    ],
                },
            )

            assert response.status_code == 201

            # Verify event was emitted
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[0][0]
            assert call_args["title"] == "Test Alert"
            assert call_args["severity"] == "high"

    def test_emit_alert_updated_is_imported(self):
        """Test that emit_alert_updated is imported in alerts API"""
        from app.api import alerts

        assert hasattr(alerts, "emit_alert_updated")
        assert callable(alerts.emit_alert_updated)
