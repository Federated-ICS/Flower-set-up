"""
WebSocket Connection Manager
Handles WebSocket connections, rooms, and broadcasting
"""
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections and rooms"""

    def __init__(self):
        # List of all active connections
        self.active_connections: List[WebSocket] = []
        # Map of room name to list of connections
        self.rooms: Dict[str, List[WebSocket]] = {}

    def connect(self, websocket: WebSocket, room: str | None = None):
        """Add a new WebSocket connection"""
        self.active_connections.append(websocket)

        # Add to room if specified
        if room:
            if room not in self.rooms:
                self.rooms[room] = []
            self.rooms[room].append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        # Remove from active connections
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # Remove from all rooms
        for room_connections in self.rooms.values():
            if websocket in room_connections:
                room_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            await connection.send_json(message)

    async def broadcast_to_room(self, room: str, message: dict):
        """Broadcast message to all clients in a specific room"""
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_json(message)

    def get_room_connections(self, room: str) -> List[WebSocket]:
        """Get all connections in a specific room"""
        return self.rooms.get(room, [])


# Global connection manager instance
manager = ConnectionManager()
