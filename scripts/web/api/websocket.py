"""
WebSocket API for real-time file change notifications.

Broadcasts file change events to connected clients.
"""

import asyncio
import json
import logging
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from web.services.file_watcher import FileChangeEvent

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections and broadcast messages."""

    def __init__(self) -> None:
        """Initialize the connection manager."""
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection
        """
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.debug(f"WebSocket connected. Total connections: {len(self._connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection
        """
        async with self._lock:
            self._connections.discard(websocket)
        logger.debug(f"WebSocket disconnected. Total connections: {len(self._connections)}")

    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected clients.

        Args:
            message: The message to broadcast
        """
        if not self._connections:
            return

        json_message = json.dumps(message)
        dead_connections = set()

        async with self._lock:
            for connection in self._connections:
                try:
                    await connection.send_text(json_message)
                except Exception as e:
                    logger.warning(f"Failed to send message: {e}")
                    dead_connections.add(connection)

            # Remove dead connections
            self._connections -= dead_connections

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)


# Global connection manager instance
manager = ConnectionManager()


def broadcast_file_change(event: FileChangeEvent) -> None:
    """Broadcast a file change event to all connected clients.

    This is called synchronously from the file watcher thread,
    so we need to schedule the async broadcast.

    Args:
        event: The file change event
    """
    message = {
        "type": "file_change",
        "event_type": event.event_type,
        "entity": event.entity_type,
        "slug": event.slug,
    }

    # Schedule the broadcast in the event loop
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(message))
    except RuntimeError:
        # No running event loop, log and skip
        logger.debug(f"No event loop for broadcast: {message}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for file change notifications.

    Clients connect here to receive real-time updates when
    campaign files are created, modified, or deleted.

    Message format:
        {
            "type": "file_change",
            "event_type": "created" | "modified" | "deleted",
            "entity": "npcs" | "locations" | "sessions" | ...,
            "slug": "file-name"
        }
    """
    await manager.connect(websocket)
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to campaign file watcher",
        })

        # Keep connection alive, handle incoming messages (if any)
        while True:
            try:
                # Wait for messages (ping/pong or client requests)
                data = await websocket.receive_text()

                # Handle ping
                if data == "ping":
                    await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                break

    finally:
        await manager.disconnect(websocket)
