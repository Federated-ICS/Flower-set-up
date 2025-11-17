"""
TDD Tests for Alerts API

Write tests first, then implement the API endpoints to make them pass.
"""
from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestAlertsAPI:
    """Test suite for /api/alerts endpoints"""

    @pytest.mark.asyncio
    async def test_get_alerts_empty(self, client: AsyncClient):
        """Test GET /api/alerts returns empty list when no alerts"""
        response = await client.get("/api/alerts")

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert data["alerts"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_alert(self, client: AsyncClient):
        """Test POST /api/alerts creates a new alert"""
        alert_data = {
            "facility_id": "facility_a",
            "severity": "critical",
            "title": "Test Alert",
            "description": "Test description",
            "sources": [
                {
                    "layer": 1,
                    "model_name": "LSTM Autoencoder",
                    "confidence": 0.95,
                    "detection_time": datetime.utcnow().isoformat(),
                    "evidence": "Anomaly detected",
                    "context_evidence": {"score": 0.95},
                }
            ],
        }

        response = await client.post("/api/alerts", json=alert_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Alert"
        assert data["severity"] == "critical"
        assert data["facility_id"] == "facility_a"
        assert data["status"] == "new"
        assert "id" in data
        assert len(data["sources"]) == 1

    @pytest.mark.asyncio
    async def test_get_alerts_with_data(self, client: AsyncClient):
        """Test GET /api/alerts returns alerts after creation"""
        # Create an alert first
        alert_data = {
            "facility_id": "facility_a",
            "severity": "high",
            "title": "Port Scan",
            "description": "Port scan detected",
            "sources": [
                {
                    "layer": 1,
                    "model_name": "Isolation Forest",
                    "confidence": 0.88,
                    "detection_time": datetime.utcnow().isoformat(),
                    "evidence": "Suspicious activity",
                }
            ],
        }
        await client.post("/api/alerts", json=alert_data)

        # Get alerts
        response = await client.get("/api/alerts")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["title"] == "Port Scan"

    @pytest.mark.asyncio
    async def test_get_alert_by_id(self, client: AsyncClient):
        """Test GET /api/alerts/{id} returns specific alert"""
        # Create alert
        alert_data = {
            "facility_id": "facility_b",
            "severity": "medium",
            "title": "DNS Anomaly",
            "description": "Unusual DNS traffic",
            "sources": [],
        }
        create_response = await client.post("/api/alerts", json=alert_data)
        alert_id = create_response.json()["id"]

        # Get by ID
        response = await client.get(f"/api/alerts/{alert_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == alert_id
        assert data["title"] == "DNS Anomaly"

    @pytest.mark.asyncio
    async def test_get_alert_not_found(self, client: AsyncClient):
        """Test GET /api/alerts/{id} returns 404 for non-existent alert"""
        fake_id = str(uuid4())
        response = await client.get(f"/api/alerts/{fake_id}")

        assert response.status_code == 404
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_update_alert_status(self, client: AsyncClient):
        """Test PUT /api/alerts/{id}/status updates alert status"""
        # Create alert
        alert_data = {
            "facility_id": "facility_c",
            "severity": "low",
            "title": "Test Alert",
            "description": "Test",
            "sources": [],
        }
        create_response = await client.post("/api/alerts", json=alert_data)
        alert_id = create_response.json()["id"]

        # Update status
        response = await client.put(
            f"/api/alerts/{alert_id}/status", json={"status": "acknowledged"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "acknowledged"
        assert data["id"] == alert_id

    @pytest.mark.asyncio
    async def test_update_alert_status_invalid(self, client: AsyncClient):
        """Test PUT /api/alerts/{id}/status rejects invalid status"""
        # Create alert
        alert_data = {
            "facility_id": "facility_a",
            "severity": "high",
            "title": "Test",
            "description": "Test",
            "sources": [],
        }
        create_response = await client.post("/api/alerts", json=alert_data)
        alert_id = create_response.json()["id"]

        # Try invalid status
        response = await client.put(
            f"/api/alerts/{alert_id}/status", json={"status": "invalid_status"}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_alerts_with_filters(self, client: AsyncClient):
        """Test GET /api/alerts with filtering parameters"""
        # Create multiple alerts
        alerts = [
            {
                "facility_id": "facility_a",
                "severity": "critical",
                "title": "Critical Alert 1",
                "description": "Test",
                "sources": [],
            },
            {
                "facility_id": "facility_b",
                "severity": "high",
                "title": "High Alert 1",
                "description": "Test",
                "sources": [],
            },
            {
                "facility_id": "facility_a",
                "severity": "medium",
                "title": "Medium Alert 1",
                "description": "Test",
                "sources": [],
            },
        ]

        for alert in alerts:
            await client.post("/api/alerts", json=alert)

        # Filter by severity
        response = await client.get("/api/alerts?severity=critical")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["alerts"][0]["severity"] == "critical"

        # Filter by facility
        response = await client.get("/api/alerts?facility=facility_a")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_get_alerts_with_pagination(self, client: AsyncClient):
        """Test GET /api/alerts pagination"""
        # Create 15 alerts
        for i in range(15):
            alert_data = {
                "facility_id": "facility_a",
                "severity": "medium",
                "title": f"Alert {i}",
                "description": "Test",
                "sources": [],
            }
            await client.post("/api/alerts", json=alert_data)

        # Get first page (limit 10)
        response = await client.get("/api/alerts?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["alerts"]) == 10
        assert data["page"] == 1
        assert data["pages"] == 2

        # Get second page
        response = await client.get("/api/alerts?page=2&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) == 5
        assert data["page"] == 2

    @pytest.mark.asyncio
    async def test_get_alerts_with_search(self, client: AsyncClient):
        """Test GET /api/alerts with search parameter"""
        # Create alerts with different titles
        alerts = [
            {
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Port Scan Detected",
                "description": "Scanning activity",
                "sources": [],
            },
            {
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Brute Force Attack",
                "description": "Login attempts",
                "sources": [],
            },
        ]

        for alert in alerts:
            await client.post("/api/alerts", json=alert)

        # Search for "Port"
        response = await client.get("/api/alerts?search=Port")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Port" in data["alerts"][0]["title"]

    @pytest.mark.asyncio
    async def test_get_alert_stats(self, client: AsyncClient):
        """Test GET /api/alerts/stats returns statistics"""
        # Create alerts with different severities and statuses
        alerts = [
            {
                "facility_id": "facility_a",
                "severity": "critical",
                "title": "Alert 1",
                "description": "Test",
                "sources": [],
            },
            {
                "facility_id": "facility_a",
                "severity": "critical",
                "title": "Alert 2",
                "description": "Test",
                "sources": [],
            },
            {
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Alert 3",
                "description": "Test",
                "sources": [],
            },
            {
                "facility_id": "facility_a",
                "severity": "medium",
                "title": "Alert 4",
                "description": "Test",
                "sources": [],
            },
        ]

        for alert in alerts:
            create_response = await client.post("/api/alerts", json=alert)
            # Mark one as false positive
            if alert["title"] == "Alert 4":
                alert_id = create_response.json()["id"]
                await client.put(
                    f"/api/alerts/{alert_id}/status", json={"status": "false-positive"}
                )

        # Get stats
        response = await client.get("/api/alerts/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert data["critical"] == 2
        assert data["unresolved"] == 3  # 3 are still new
        assert data["false_positives"] == 1
