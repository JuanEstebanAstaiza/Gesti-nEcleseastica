from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)
        await websocket.send_json({"type": "welcome", "message": "Conectado a notificaciones"})

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, payload: dict):
        for ws in list(self.active):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"type": "echo", "message": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

