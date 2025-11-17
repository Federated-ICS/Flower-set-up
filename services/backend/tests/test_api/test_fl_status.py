"""
TDD Tests for FL Status API
"""
import pytest
from httpx import AsyncClient


class TestFLStatusAPI:
    """Test suite for /api/fl endpoints"""

    @pytest.mark.asyncio
    async def test_get_current_round_none(self, client: AsyncClient):
        """Test GET /api/fl/rounds/current returns null when no rounds"""
        response = await client.get("/api/fl/rounds/current")

        assert response.status_code == 200
        data = response.json()
        assert data is None or data == {}

    @pytest.mark.asyncio
    async def test_trigger_fl_round(self, client: AsyncClient):
        """Test POST /api/fl/rounds/trigger creates new round"""
        response = await client.post("/api/fl/rounds/trigger")

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "round_number" in data
        assert data["round_number"] == 1
        assert data["status"] == "in-progress"
        assert data["phase"] == "distributing"
        assert data["progress"] == 0
        assert len(data["clients"]) == 2  # 2 facilities

    @pytest.mark.asyncio
    async def test_get_current_round_exists(self, client: AsyncClient):
        """Test GET /api/fl/rounds/current returns active round"""
        # Create a round
        await client.post("/api/fl/rounds/trigger")

        # Get current round
        response = await client.get("/api/fl/rounds/current")

        assert response.status_code == 200
        data = response.json()
        assert data["round_number"] == 1
        assert data["status"] == "in-progress"
        assert "clients" in data
        assert len(data["clients"]) == 2

    @pytest.mark.asyncio
    async def test_get_round_by_id(self, client: AsyncClient):
        """Test GET /api/fl/rounds/{id} returns specific round"""
        # Create round
        create_response = await client.post("/api/fl/rounds/trigger")
        round_id = create_response.json()["id"]

        # Get by ID
        response = await client.get(f"/api/fl/rounds/{round_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == round_id
        assert data["round_number"] == 1

    @pytest.mark.asyncio
    async def test_get_round_not_found(self, client: AsyncClient):
        """Test GET /api/fl/rounds/{id} returns 404 for non-existent round"""
        response = await client.get("/api/fl/rounds/999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_all_rounds(self, client: AsyncClient):
        """Test GET /api/fl/rounds returns all rounds"""
        # Create multiple rounds
        await client.post("/api/fl/rounds/trigger")
        await client.post("/api/fl/rounds/trigger")

        response = await client.get("/api/fl/rounds")

        assert response.status_code == 200
        data = response.json()
        assert "rounds" in data
        assert len(data["rounds"]) == 2

    @pytest.mark.asyncio
    async def test_get_rounds_with_pagination(self, client: AsyncClient):
        """Test GET /api/fl/rounds with pagination"""
        # Create 5 rounds
        for _ in range(5):
            await client.post("/api/fl/rounds/trigger")

        # Get first page
        response = await client.get("/api/fl/rounds?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["rounds"]) == 3

    @pytest.mark.asyncio
    async def test_get_fl_clients(self, client: AsyncClient):
        """Test GET /api/fl/clients returns all clients"""
        # Create a round
        await client.post("/api/fl/rounds/trigger")

        response = await client.get("/api/fl/clients")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        # Check client structure
        client_data = data[0]
        assert "id" in client_data
        assert "facility_id" in client_data
        assert "name" in client_data
        assert "status" in client_data
        assert "progress" in client_data
        assert "current_epoch" in client_data
        assert "total_epochs" in client_data

    @pytest.mark.asyncio
    async def test_get_client_by_id(self, client: AsyncClient):
        """Test GET /api/fl/clients/{id} returns specific client"""
        # Create round
        round_response = await client.post("/api/fl/rounds/trigger")
        client_id = round_response.json()["clients"][0]["id"]

        # Get client
        response = await client.get(f"/api/fl/clients/{client_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == client_id

    @pytest.mark.asyncio
    async def test_update_client_progress(self, client: AsyncClient):
        """Test PUT /api/fl/clients/{id} updates client progress"""
        # Create round
        round_response = await client.post("/api/fl/rounds/trigger")
        client_id = round_response.json()["clients"][0]["id"]

        # Update client
        update_data = {"progress": 50, "current_epoch": 5, "loss": 0.15, "accuracy": 92.5}
        response = await client.put(f"/api/fl/clients/{client_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 50
        assert data["current_epoch"] == 5
        assert data["loss"] == 0.15
        assert data["accuracy"] == 92.5

    @pytest.mark.asyncio
    async def test_update_round_progress(self, client: AsyncClient):
        """Test PUT /api/fl/rounds/{id}/progress updates round"""
        # Create round
        create_response = await client.post("/api/fl/rounds/trigger")
        round_id = create_response.json()["id"]

        # Update progress
        update_data = {"progress": 75, "phase": "training"}
        response = await client.put(f"/api/fl/rounds/{round_id}/progress", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 75
        assert data["phase"] == "training"

    @pytest.mark.asyncio
    async def test_complete_round(self, client: AsyncClient):
        """Test POST /api/fl/rounds/{id}/complete marks round as complete"""
        # Create round
        create_response = await client.post("/api/fl/rounds/trigger")
        round_id = create_response.json()["id"]

        # Complete round
        complete_data = {"model_accuracy": 95.5}
        response = await client.post(f"/api/fl/rounds/{round_id}/complete", json=complete_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["phase"] == "complete"
        assert data["progress"] == 100
        assert data["model_accuracy"] == 95.5
        assert data["end_time"] is not None

    @pytest.mark.asyncio
    async def test_get_privacy_metrics(self, client: AsyncClient):
        """Test GET /api/fl/privacy-metrics returns privacy info"""
        response = await client.get("/api/fl/privacy-metrics")

        assert response.status_code == 200
        data = response.json()
        assert "epsilon" in data
        assert "delta" in data
        assert "data_size" in data
        assert "encryption" in data
        assert "privacy_budget_remaining" in data

        # Check values are reasonable
        assert isinstance(data["epsilon"], float)
        assert data["epsilon"] > 0

    @pytest.mark.asyncio
    async def test_multiple_rounds_sequence(self, client: AsyncClient):
        """Test creating multiple rounds in sequence"""
        # Create first round
        response1 = await client.post("/api/fl/rounds/trigger")
        assert response1.json()["round_number"] == 1

        # Create second round
        response2 = await client.post("/api/fl/rounds/trigger")
        assert response2.json()["round_number"] == 2

        # Get current should return latest
        current = await client.get("/api/fl/rounds/current")
        assert current.json()["round_number"] == 2
