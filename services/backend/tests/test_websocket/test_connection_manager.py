"""
Tests for WebSocket Connection Manager
Following TDD approach - these tests will fail initially
"""
import pytest


class TestConnectionManager:
    """Test WebSocket connection management"""

    def test_manager_initialization(self):
        """Test that ConnectionManager can be initialized"""
        from app.websocket.manager import ConnectionManager

        manager = ConnectionManager()
        assert manager is not None
        assert manager.active_connections == []

    def test_connect_adds_connection(self):
        """Test that connect() adds a WebSocket to active connections"""
        from app.websocket.manager import ConnectionManager

        manager = ConnectionManager()
        mock_websocket = MockWebSocket()

        manager.connect(mock_websocket)

        assert len(manager.active_connections) == 1
        assert mock_websocket in manager.active_connections

    def test_disconnect_removes_connection(self):
        """Test that disconnect() removes a WebSocket from active connections"""
        from app.websocket.manager import ConnectionManager

        manager = ConnectionManager()
        mock_websocket = MockWebSocket()

        manager.connect(mock_websocket)
        manager.disconnect(mock_websocket)

        assert len(manager.active_connections) == 0
        assert mock_websocket not in manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_connections(self):
        """Test that broadcast() sends message to all connected clients"""
        from app.websocket.manager import ConnectionManager

        manager = ConnectionManager()
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()

        manager.connect(mock_ws1)
        manager.connect(mock_ws2)

        test_message = {"type": "test", "data": "hello"}
        await manager.broadcast(test_message)

        assert mock_ws1.sent_messages == [test_message]
        assert mock_ws2.sent_messages == [test_message]

    @pytest.mark.asyncio
    async def test_broadcast_to_room_sends_only_to_room_members(self):
        """Test that broadcast_to_room() sends only to specific room"""
        from app.websocket.manager import ConnectionManager

        manager = ConnectionManager()
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()
        mock_ws3 = MockWebSocket()

        manager.connect(mock_ws1, room="alerts")
        manager.connect(mock_ws2, room="alerts")
        manager.connect(mock_ws3, room="fl-status")

        test_message = {"type": "alert", "data": "new alert"}
        await manager.broadcast_to_room("alerts", test_message)

        assert mock_ws1.sent_messages == [test_message]
        assert mock_ws2.sent_messages == [test_message]
        assert mock_ws3.sent_messages == []

    def test_get_room_connections_returns_correct_connections(self):
        """Test that get_room_connections() returns only connections in that room"""
        from app.websocket.manager import ConnectionManager

        manager = ConnectionManager()
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()
        mock_ws3 = MockWebSocket()

        manager.connect(mock_ws1, room="alerts")
        manager.connect(mock_ws2, room="alerts")
        manager.connect(mock_ws3, room="fl-status")

        alerts_connections = manager.get_room_connections("alerts")

        assert len(alerts_connections) == 2
        assert mock_ws1 in alerts_connections
        assert mock_ws2 in alerts_connections
        assert mock_ws3 not in alerts_connections


# Mock WebSocket for testing
class MockWebSocket:
    """Mock WebSocket for testing without actual connections"""

    def __init__(self):
        self.sent_messages = []
        self.is_closed = False

    async def send_json(self, data):
        """Mock send_json method"""
        if not self.is_closed:
            self.sent_messages.append(data)

    async def accept(self):
        """Mock accept method"""
        pass

    async def close(self):
        """Mock close method"""
        self.is_closed = True
