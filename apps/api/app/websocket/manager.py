import json
from typing import Dict, List
from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps auction_id -> list of active websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, auction_id: str):
        await websocket.accept()
        if auction_id not in self.active_connections:
            self.active_connections[auction_id] = []
        self.active_connections[auction_id].append(websocket)
        logger.info("websocket_connected", auction_id=auction_id)

    def disconnect(self, websocket: WebSocket, auction_id: str):
        if auction_id in self.active_connections:
            if websocket in self.active_connections[auction_id]:
                self.active_connections[auction_id].remove(websocket)
            if not self.active_connections[auction_id]:
                del self.active_connections[auction_id]
        logger.info("websocket_disconnected", auction_id=auction_id)

    async def broadcast_to_auction(self, auction_id: str, message: dict):
        if auction_id in self.active_connections:
            # We must handle cases where sending fails because client disconnected
            dead_connections = []
            for connection in self.active_connections[auction_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    dead_connections.append(connection)
            
            for dead in dead_connections:
                self.disconnect(dead, auction_id)

manager = ConnectionManager()
