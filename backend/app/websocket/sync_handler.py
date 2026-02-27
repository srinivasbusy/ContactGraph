import json
import logging
from typing import Dict, Any

from fastapi import WebSocket, WebSocketDisconnect

from app.services.neo4j_service import Neo4jService
from app.services.contact_service import ContactService

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections keyed by user phone."""

    def __init__(self) -> None:
        self._active: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_phone: str) -> None:
        await websocket.accept()
        self._active[user_phone] = websocket
        logger.info("WS connected: %s (total=%d)", user_phone, len(self._active))

    def disconnect(self, user_phone: str) -> None:
        self._active.pop(user_phone, None)
        logger.info("WS disconnected: %s (total=%d)", user_phone, len(self._active))

    async def send_personal(self, user_phone: str, message: Dict[str, Any]) -> None:
        ws = self._active.get(user_phone)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        for ws in list(self._active.values()):
            try:
                await ws.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


async def handle_sync_message(
    websocket: WebSocket,
    user_phone: str,
    raw_message: str,
    neo4j: Neo4jService,
) -> None:
    """
    Process a message received over the WebSocket.

    Expected message format:
    {
        "type": "sync_contacts",
        "contacts": [{"phone": "+1...", "name": "Alice"}, ...]
    }
    """
    try:
        message: Dict[str, Any] = json.loads(raw_message)
    except json.JSONDecodeError:
        await websocket.send_json({"type": "error", "detail": "Invalid JSON."})
        return

    msg_type = message.get("type")

    if msg_type == "sync_contacts":
        contacts = message.get("contacts", [])
        if not isinstance(contacts, list):
            await websocket.send_json({"type": "error", "detail": "'contacts' must be a list."})
            return
        service = ContactService(neo4j)
        result = service.sync(user_phone, contacts)
        await websocket.send_json(
            {"type": "sync_result", "synced": result.get("synced", 0)}
        )
    elif msg_type == "ping":
        await websocket.send_json({"type": "pong"})
    else:
        await websocket.send_json(
            {"type": "error", "detail": f"Unknown message type: '{msg_type}'."}
        )
