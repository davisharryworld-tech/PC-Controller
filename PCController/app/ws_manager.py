import json
from datetime import datetime, timezone
from typing import Set
from fastapi import WebSocket
from app.logger import logger
from app.schemas import WSMessageOut


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        client_host = websocket.client.host if websocket.client else "unknown"
        logger.info(f"WebSocket client connected: {client_host} (Total active: {len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        client_host = websocket.client.host if websocket.client else "unknown"
        logger.info(f"WebSocket client disconnected: {client_host} (Remaining active: {len(self.active_connections)})")

    async def send_message(self, websocket: WebSocket, message: WSMessageOut) -> None:
        await websocket.send_text(message.model_dump_json())

    async def broadcast(self, message: WSMessageOut) -> None:
        text = message.model_dump_json()
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(text)
            except Exception as e:
                logger.warning(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        for dead_conn in disconnected:
            self.disconnect(dead_conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


ws_manager = ConnectionManager()

