"""
Event Emitter for WebSocket
Provides functions to emit events to connected clients
"""
import logging

from app.websocket.manager import manager

logger = logging.getLogger(__name__)


class EventType:
    """Event type constants"""

    ALERT_CREATED = "alert_created"
    ALERT_UPDATED = "alert_updated"
    FL_PROGRESS = "fl_progress"
    ATTACK_DETECTED = "attack_detected"
    DASHBOARD_UPDATE = "dashboard_update"


class Room:
    """Room name constants"""

    ALERTS = "alerts"
    FL_STATUS = "fl-status"
    ATTACK_GRAPH = "attack-graph"
    DASHBOARD = "dashboard"


async def emit_alert_created(alert_data: dict):
    """
    Emit alert_created event to alerts room AND dashboard room
    Called when a new alert is created
    """
    try:
        message = {"type": EventType.ALERT_CREATED, "data": alert_data}

        # Send to alerts page
        await manager.broadcast_to_room(Room.ALERTS, message)

        # Send to dashboard page
        await manager.broadcast_to_room(Room.DASHBOARD, message)

        logger.info(f"Emitted alert_created event to alerts & dashboard: {alert_data.get('id')}")
    except Exception as e:
        logger.error(f"Error emitting alert_created event: {e}")


async def emit_alert_updated(alert_data: dict):
    """
    Emit alert_updated event to alerts room AND dashboard room
    Called when an alert status is updated
    """
    try:
        message = {"type": EventType.ALERT_UPDATED, "data": alert_data}

        # Send to alerts page
        await manager.broadcast_to_room(Room.ALERTS, message)

        # Send to dashboard page
        await manager.broadcast_to_room(Room.DASHBOARD, message)

        logger.info(f"Emitted alert_updated event to alerts & dashboard: {alert_data.get('id')}")
    except Exception as e:
        logger.error(f"Error emitting alert_updated event: {e}")


async def emit_fl_progress(progress_data: dict):
    """
    Emit fl_progress event to FL status room AND dashboard room
    Called when FL training progress updates
    """
    try:
        message = {"type": EventType.FL_PROGRESS, "data": progress_data}

        # Send to FL status page
        await manager.broadcast_to_room(Room.FL_STATUS, message)

        # Send to dashboard page
        await manager.broadcast_to_room(Room.DASHBOARD, message)

        round_id = progress_data.get("round_id")
        logger.info(f"Emitted fl_progress event to fl-status & dashboard: Round {round_id}")
    except Exception as e:
        logger.error(f"Error emitting fl_progress event: {e}")


async def emit_attack_detected(attack_data: dict):
    """
    Emit attack_detected event to attack graph room AND dashboard room
    Called when a new attack technique is detected
    """
    try:
        message = {"type": EventType.ATTACK_DETECTED, "data": attack_data}

        # Send to attack graph page
        await manager.broadcast_to_room(Room.ATTACK_GRAPH, message)

        # Send to dashboard page
        await manager.broadcast_to_room(Room.DASHBOARD, message)

        technique_id = attack_data.get("technique_id")
        logger.info(f"Emitted attack_detected event to attack-graph & dashboard: {technique_id}")
    except Exception as e:
        logger.error(f"Error emitting attack_detected event: {e}")


async def emit_dashboard_update(stats_data: dict):
    """
    Emit dashboard_update event to all clients
    Called when dashboard statistics change
    """
    try:
        await manager.broadcast({"type": EventType.DASHBOARD_UPDATE, "data": stats_data})
        logger.info("Emitted dashboard_update event")
    except Exception as e:
        logger.error(f"Error emitting dashboard_update event: {e}")
