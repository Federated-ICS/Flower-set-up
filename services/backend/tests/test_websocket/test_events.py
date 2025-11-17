"""
Tests for WebSocket Event Emitters
Following TDD approach - RED phase
"""
from unittest.mock import AsyncMock, patch

import pytest


class TestEventEmitter:
    """Test event emission functionality"""

    @pytest.mark.asyncio
    async def test_emit_alert_created_event(self):
        """Test that alert_created event is emitted to alerts AND dashboard rooms"""
        from app.events.emitter import emit_alert_created

        alert_data = {
            "id": "alert-123",
            "title": "Suspicious Activity",
            "severity": "high",
        }

        # Mock the manager to verify broadcast was called
        with patch("app.events.emitter.manager") as mock_manager:
            mock_manager.broadcast_to_room = AsyncMock()

            await emit_alert_created(alert_data)

            # Verify broadcast was called TWICE (alerts + dashboard)
            assert mock_manager.broadcast_to_room.call_count == 2

            # Check first call (alerts room)
            first_call = mock_manager.broadcast_to_room.call_args_list[0]
            assert first_call[0][0] == "alerts"
            assert first_call[0][1]["type"] == "alert_created"
            assert first_call[0][1]["data"] == alert_data

            # Check second call (dashboard room)
            second_call = mock_manager.broadcast_to_room.call_args_list[1]
            assert second_call[0][0] == "dashboard"
            assert second_call[0][1]["type"] == "alert_created"
            assert second_call[0][1]["data"] == alert_data

    @pytest.mark.asyncio
    async def test_emit_alert_updated_event(self):
        """Test that alert_updated event is emitted to alerts AND dashboard rooms"""
        from app.events.emitter import emit_alert_updated

        alert_data = {
            "id": "alert-123",
            "status": "acknowledged",
        }

        with patch("app.events.emitter.manager") as mock_manager:
            mock_manager.broadcast_to_room = AsyncMock()

            await emit_alert_updated(alert_data)

            # Verify broadcast was called TWICE (alerts + dashboard)
            assert mock_manager.broadcast_to_room.call_count == 2

            # Check first call (alerts room)
            first_call = mock_manager.broadcast_to_room.call_args_list[0]
            assert first_call[0][0] == "alerts"
            assert first_call[0][1]["type"] == "alert_updated"

            # Check second call (dashboard room)
            second_call = mock_manager.broadcast_to_room.call_args_list[1]
            assert second_call[0][0] == "dashboard"
            assert second_call[0][1]["type"] == "alert_updated"

    @pytest.mark.asyncio
    async def test_emit_fl_progress_event(self):
        """Test that fl_progress event is emitted to fl-status AND dashboard rooms"""
        from app.events.emitter import emit_fl_progress

        progress_data = {
            "round_id": 1,
            "progress": 75,
            "phase": "training",
        }

        with patch("app.events.emitter.manager") as mock_manager:
            mock_manager.broadcast_to_room = AsyncMock()

            await emit_fl_progress(progress_data)

            # Verify broadcast was called TWICE (fl-status + dashboard)
            assert mock_manager.broadcast_to_room.call_count == 2

            # Check first call (fl-status room)
            first_call = mock_manager.broadcast_to_room.call_args_list[0]
            assert first_call[0][0] == "fl-status"
            assert first_call[0][1]["type"] == "fl_progress"

            # Check second call (dashboard room)
            second_call = mock_manager.broadcast_to_room.call_args_list[1]
            assert second_call[0][0] == "dashboard"
            assert second_call[0][1]["type"] == "fl_progress"

    @pytest.mark.asyncio
    async def test_emit_attack_detected_event(self):
        """Test that attack_detected event is emitted to attack-graph AND dashboard rooms"""
        from app.events.emitter import emit_attack_detected

        attack_data = {
            "technique_id": "T0800",
            "name": "Activate Firmware Update Mode",
            "probability": 0.95,
        }

        with patch("app.events.emitter.manager") as mock_manager:
            mock_manager.broadcast_to_room = AsyncMock()

            await emit_attack_detected(attack_data)

            # Verify broadcast was called TWICE (attack-graph + dashboard)
            assert mock_manager.broadcast_to_room.call_count == 2

            # Check first call (attack-graph room)
            first_call = mock_manager.broadcast_to_room.call_args_list[0]
            assert first_call[0][0] == "attack-graph"
            assert first_call[0][1]["type"] == "attack_detected"

            # Check second call (dashboard room)
            second_call = mock_manager.broadcast_to_room.call_args_list[1]
            assert second_call[0][0] == "dashboard"
            assert second_call[0][1]["type"] == "attack_detected"

    @pytest.mark.asyncio
    async def test_emit_dashboard_update_event(self):
        """Test that dashboard_update event is emitted to all clients"""
        from app.events.emitter import emit_dashboard_update

        stats_data = {
            "active_alerts": 5,
            "fl_progress": 80,
            "threats_detected": 3,
        }

        with patch("app.events.emitter.manager") as mock_manager:
            mock_manager.broadcast = AsyncMock()

            await emit_dashboard_update(stats_data)

            # Dashboard updates go to all clients, not a specific room
            mock_manager.broadcast.assert_called_once()
            call_args = mock_manager.broadcast.call_args
            assert call_args[0][0]["type"] == "dashboard_update"
            assert call_args[0][0]["data"] == stats_data

    @pytest.mark.asyncio
    async def test_emit_handles_errors_gracefully(self):
        """Test that emit functions handle errors without crashing"""
        from app.events.emitter import emit_alert_created

        alert_data = {"id": "alert-123"}

        # Mock manager to raise an exception
        with patch("app.events.emitter.manager") as mock_manager:
            mock_manager.broadcast_to_room = AsyncMock(side_effect=Exception("Connection error"))

            # Should not raise exception
            try:
                await emit_alert_created(alert_data)
            except Exception:
                pytest.fail("emit_alert_created should handle errors gracefully")

    def test_event_types_are_defined(self):
        """Test that event type constants are defined"""
        from app.events.emitter import EventType

        assert hasattr(EventType, "ALERT_CREATED")
        assert hasattr(EventType, "ALERT_UPDATED")
        assert hasattr(EventType, "FL_PROGRESS")
        assert hasattr(EventType, "ATTACK_DETECTED")
        assert hasattr(EventType, "DASHBOARD_UPDATE")

    def test_room_names_are_defined(self):
        """Test that room name constants are defined"""
        from app.events.emitter import Room

        assert hasattr(Room, "ALERTS")
        assert hasattr(Room, "FL_STATUS")
        assert hasattr(Room, "ATTACK_GRAPH")
        assert hasattr(Room, "DASHBOARD")
