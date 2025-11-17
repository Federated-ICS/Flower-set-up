"""
TDD Tests for Predictions API
"""
import pytest
from httpx import AsyncClient


class TestPredictionsAPI:
    """Test suite for /api/predictions endpoints"""

    @pytest.mark.asyncio
    async def test_get_predictions_empty(self, client: AsyncClient):
        """Test GET /api/predictions returns empty list"""
        response = await client.get("/api/predictions")

        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert data["predictions"] == []

    @pytest.mark.asyncio
    async def test_create_prediction(self, client: AsyncClient):
        """Test POST /api/predictions creates new prediction"""
        # First create an alert to link to
        alert_data = {
            "facility_id": "facility_a",
            "severity": "high",
            "title": "Port Scan",
            "description": "Test",
            "attack_type": "T0846",
            "attack_name": "Port Scan",
            "sources": [],
        }
        alert_response = await client.post("/api/alerts", json=alert_data)
        alert_id = alert_response.json()["id"]

        # Create prediction
        prediction_data = {
            "current_technique": "T0846",
            "current_technique_name": "Port Scan",
            "alert_id": alert_id,
            "predicted_techniques": [
                {
                    "technique_id": "T0800",
                    "technique_name": "Lateral Movement",
                    "probability": 0.72,
                    "rank": 1,
                    "timeframe": "15-60 minutes",
                },
                {
                    "technique_id": "T0817",
                    "technique_name": "Unauthorized Access",
                    "probability": 0.65,
                    "rank": 2,
                    "timeframe": "1-4 hours",
                },
            ],
        }

        response = await client.post("/api/predictions", json=prediction_data)

        assert response.status_code == 201
        data = response.json()
        assert data["current_technique"] == "T0846"
        assert data["current_technique_name"] == "Port Scan"
        assert data["alert_id"] == alert_id
        assert data["validated"] is False
        assert len(data["predicted_techniques"]) == 2
        assert data["predicted_techniques"][0]["probability"] == 0.72

    @pytest.mark.asyncio
    async def test_get_predictions_with_data(self, client: AsyncClient):
        """Test GET /api/predictions returns predictions"""
        # Create alert and prediction
        alert_response = await client.post(
            "/api/alerts",
            json={
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Test",
                "description": "Test",
                "sources": [],
            },
        )
        alert_id = alert_response.json()["id"]

        prediction_data = {
            "current_technique": "T0859",
            "current_technique_name": "Brute Force",
            "alert_id": alert_id,
            "predicted_techniques": [
                {
                    "technique_id": "T0817",
                    "technique_name": "Unauthorized Access",
                    "probability": 0.78,
                    "rank": 1,
                }
            ],
        }
        await client.post("/api/predictions", json=prediction_data)

        # Get predictions
        response = await client.get("/api/predictions")

        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 1
        assert data["predictions"][0]["current_technique"] == "T0859"

    @pytest.mark.asyncio
    async def test_get_prediction_by_id(self, client: AsyncClient):
        """Test GET /api/predictions/{id} returns specific prediction"""
        # Create alert and prediction
        alert_response = await client.post(
            "/api/alerts",
            json={
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Test",
                "description": "Test",
                "sources": [],
            },
        )

        prediction_data = {
            "current_technique": "T0885",
            "current_technique_name": "Protocol Manipulation",
            "alert_id": alert_response.json()["id"],
            "predicted_techniques": [],
        }
        create_response = await client.post("/api/predictions", json=prediction_data)
        prediction_id = create_response.json()["id"]

        # Get by ID
        response = await client.get(f"/api/predictions/{prediction_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prediction_id
        assert data["current_technique"] == "T0885"

    @pytest.mark.asyncio
    async def test_get_prediction_not_found(self, client: AsyncClient):
        """Test GET /api/predictions/{id} returns 404"""
        from uuid import uuid4

        fake_id = str(uuid4())

        response = await client.get(f"/api/predictions/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_validate_prediction(self, client: AsyncClient):
        """Test POST /api/predictions/{id}/validate marks prediction as validated"""
        # Create alert and prediction
        alert_response = await client.post(
            "/api/alerts",
            json={
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Test",
                "description": "Test",
                "sources": [],
            },
        )

        prediction_data = {
            "current_technique": "T0846",
            "current_technique_name": "Port Scan",
            "alert_id": alert_response.json()["id"],
            "predicted_techniques": [],
        }
        create_response = await client.post("/api/predictions", json=prediction_data)
        prediction_id = create_response.json()["id"]

        # Validate
        response = await client.post(f"/api/predictions/{prediction_id}/validate")

        assert response.status_code == 200
        data = response.json()
        assert data["validated"] is True
        assert data["validation_time"] is not None

    @pytest.mark.asyncio
    async def test_get_predictions_filtered_by_validated(self, client: AsyncClient):
        """Test GET /api/predictions?validated=true filters correctly"""
        # Create alert
        alert_response = await client.post(
            "/api/alerts",
            json={
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Test",
                "description": "Test",
                "sources": [],
            },
        )
        alert_id = alert_response.json()["id"]

        # Create two predictions
        pred1 = await client.post(
            "/api/predictions",
            json={
                "current_technique": "T0846",
                "current_technique_name": "Port Scan",
                "alert_id": alert_id,
                "predicted_techniques": [],
            },
        )

        await client.post(
            "/api/predictions",
            json={
                "current_technique": "T0859",
                "current_technique_name": "Brute Force",
                "alert_id": alert_id,
                "predicted_techniques": [],
            },
        )

        # Validate only first one
        await client.post(f"/api/predictions/{pred1.json()['id']}/validate")

        # Filter by validated
        response = await client.get("/api/predictions?validated=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 1
        assert data["predictions"][0]["validated"] is True

        # Filter by not validated
        response = await client.get("/api/predictions?validated=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 1
        assert data["predictions"][0]["validated"] is False

    @pytest.mark.asyncio
    async def test_get_latest_prediction(self, client: AsyncClient):
        """Test GET /api/predictions/latest returns most recent"""
        # Create alert
        alert_response = await client.post(
            "/api/alerts",
            json={
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Test",
                "description": "Test",
                "sources": [],
            },
        )
        alert_id = alert_response.json()["id"]

        # Create multiple predictions
        await client.post(
            "/api/predictions",
            json={
                "current_technique": "T0846",
                "current_technique_name": "Port Scan",
                "alert_id": alert_id,
                "predicted_techniques": [],
            },
        )

        await client.post(
            "/api/predictions",
            json={
                "current_technique": "T0859",
                "current_technique_name": "Brute Force",
                "alert_id": alert_id,
                "predicted_techniques": [],
            },
        )

        # Get latest
        response = await client.get("/api/predictions/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["current_technique"] == "T0859"  # Most recent

    @pytest.mark.asyncio
    async def test_get_predictions_pagination(self, client: AsyncClient):
        """Test GET /api/predictions with pagination"""
        # Create alert
        alert_response = await client.post(
            "/api/alerts",
            json={
                "facility_id": "facility_a",
                "severity": "high",
                "title": "Test",
                "description": "Test",
                "sources": [],
            },
        )
        alert_id = alert_response.json()["id"]

        # Create 5 predictions
        for i in range(5):
            await client.post(
                "/api/predictions",
                json={
                    "current_technique": f"T{i:04d}",
                    "current_technique_name": f"Technique {i}",
                    "alert_id": alert_id,
                    "predicted_techniques": [],
                },
            )

        # Get with limit
        response = await client.get("/api/predictions?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["predictions"]) == 3
