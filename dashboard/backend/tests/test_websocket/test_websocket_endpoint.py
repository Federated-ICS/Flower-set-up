"""
Tests for WebSocket API Endpoint
Following TDD approach - RED phase
"""
from fastapi.testclient import TestClient

from app.main import app


class TestWebSocketEndpoint:
    """Test WebSocket endpoint functionality"""

    def test_websocket_endpoint_exists(self):
        """Test that /ws endpoint exists and accepts WebSocket connections"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            assert websocket is not None

    def test_websocket_accepts_connection(self):
        """Test that WebSocket connection is accepted"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Connection should be established - verify by receiving welcome message
            data = websocket.receive_json()
            assert data["type"] == "connection"

    def test_websocket_receives_welcome_message(self):
        """Test that client receives welcome message on connect"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()

            assert data["type"] == "connection"
            assert data["status"] == "connected"
            assert "message" in data

    def test_websocket_can_subscribe_to_room(self):
        """Test that client can subscribe to a specific room"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Skip welcome message
            websocket.receive_json()

            # Subscribe to alerts room
            websocket.send_json({"action": "subscribe", "room": "alerts"})

            response = websocket.receive_json()
            assert response["type"] == "subscription"
            assert response["status"] == "subscribed"
            assert response["room"] == "alerts"

    def test_websocket_can_unsubscribe_from_room(self):
        """Test that client can unsubscribe from a room"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Skip welcome message
            websocket.receive_json()

            # Subscribe first
            websocket.send_json({"action": "subscribe", "room": "alerts"})
            websocket.receive_json()

            # Then unsubscribe
            websocket.send_json({"action": "unsubscribe", "room": "alerts"})

            response = websocket.receive_json()
            assert response["type"] == "subscription"
            assert response["status"] == "unsubscribed"
            assert response["room"] == "alerts"

    def test_websocket_handles_invalid_action(self):
        """Test that invalid actions are handled gracefully"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Skip welcome message
            websocket.receive_json()

            # Send invalid action
            websocket.send_json({"action": "invalid_action"})

            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "message" in response

    def test_websocket_handles_ping_pong(self):
        """Test that WebSocket responds to ping with pong"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            # Skip welcome message
            websocket.receive_json()

            # Send ping
            websocket.send_json({"action": "ping"})

            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_multiple_clients_can_connect(self):
        """Test that multiple clients can connect simultaneously"""
        client = TestClient(app)

        with client.websocket_connect("/ws") as ws1:
            with client.websocket_connect("/ws") as ws2:
                # Both should receive welcome messages
                data1 = ws1.receive_json()
                data2 = ws2.receive_json()

                assert data1["type"] == "connection"
                assert data2["type"] == "connection"

    def test_websocket_connection_cleanup_on_disconnect(self):
        """Test that connection is properly cleaned up on disconnect"""
        from app.websocket.manager import manager

        client = TestClient(app)
        initial_count = len(manager.active_connections)

        with client.websocket_connect("/ws") as _:
            # Connection should be added
            assert len(manager.active_connections) == initial_count + 1

        # After disconnect, connection should be removed
        assert len(manager.active_connections) == initial_count
