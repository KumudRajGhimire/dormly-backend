from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
        self,
        conversation_id: str,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.active_connections[conversation_id].append(websocket)

    def disconnect(
        self,
        conversation_id: str,
        websocket: WebSocket,
    ):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)

            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def broadcast(
        self,
        conversation_id: str,
        message: dict,
    ):

        dead_connections = []
        for websocket in self.active_connections.get(conversation_id, []):
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.active_connections[conversation_id].remove(websocket)


manager = ConnectionManager()