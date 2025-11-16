"""
WebSocket API Endpoint
Handles real-time communication with clients
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication
    Supports room-based subscriptions
    """
    await websocket.accept()

    # Add to general connections
    manager.connect(websocket)

    # Send welcome message
    await websocket.send_json(
        {
            "type": "connection",
            "status": "connected",
            "message": "Connected to ICS Threat Detection",
        }
    )

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "subscribe":
                # Subscribe to a room
                room = data.get("room")
                if room:
                    manager.connect(websocket, room=room)
                    await websocket.send_json(
                        {"type": "subscription", "status": "subscribed", "room": room}
                    )

            elif action == "unsubscribe":
                # Unsubscribe from a room
                room = data.get("room")
                if room and room in manager.rooms:
                    if websocket in manager.rooms[room]:
                        manager.rooms[room].remove(websocket)
                    await websocket.send_json(
                        {"type": "subscription", "status": "unsubscribed", "room": room}
                    )

            elif action == "ping":
                # Respond to ping
                await websocket.send_json({"type": "pong"})

            else:
                # Invalid action
                await websocket.send_json({"type": "error", "message": f"Unknown action: {action}"})

    except WebSocketDisconnect:
        # Clean up on disconnect
        manager.disconnect(websocket)
