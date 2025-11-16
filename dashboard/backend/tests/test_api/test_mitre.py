from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMitreAPI:
    def test_get_attack_graph(self):
        """Test getting the attack graph"""
        response = client.get("/api/mitre/graph")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "links" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["links"], list)

        # Verify node structure
        if data["nodes"]:
            node = data["nodes"][0]
            assert "id" in node
            assert "name" in node
            assert "type" in node
            assert "probability" in node
            assert node["type"] in ["current", "predicted"]

    def test_get_all_techniques(self):
        """Test getting all techniques"""
        response = client.get("/api/mitre/techniques")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Should have techniques from import
        assert len(data) > 0

        # Verify technique structure
        technique = data[0]
        assert "id" in technique
        assert "name" in technique
        assert "description" in technique
        assert "platforms" in technique
        assert "tactics" in technique

    def test_get_technique_details_valid(self):
        """Test getting details for a valid technique"""
        # First get a valid technique ID
        response = client.get("/api/mitre/techniques")
        assert response.status_code == 200
        techniques = response.json()

        if techniques:
            technique_id = techniques[0]["id"]

            # Get details for that technique
            response = client.get(f"/api/mitre/technique/{technique_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == technique_id
            assert "name" in data
            assert "description" in data
            assert "platforms" in data
            assert "tactics" in data

    def test_get_technique_not_found(self):
        """Test getting details for non-existent technique"""
        response = client.get("/api/mitre/technique/INVALID999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_attack_graph_has_current_attacks(self):
        """Test that attack graph includes detected techniques"""
        response = client.get("/api/mitre/graph")
        assert response.status_code == 200
        data = response.json()

        current_nodes = [n for n in data["nodes"] if n["type"] == "current"]
        # Should have at least some detected techniques from import
        assert len(current_nodes) > 0

        # Current attacks should have probability 1.0
        for node in current_nodes:
            assert node["probability"] == 1.0

    def test_attack_graph_links_structure(self):
        """Test that links have correct structure"""
        response = client.get("/api/mitre/graph")
        assert response.status_code == 200
        data = response.json()

        if data["links"]:
            link = data["links"][0]
            assert "source" in link
            assert "target" in link
            assert "probability" in link
            assert 0 <= link["probability"] <= 1
