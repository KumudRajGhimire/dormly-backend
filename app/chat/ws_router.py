from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.chat.service import get_conversation
from app.chat.websocket import manager
from app.core.security import decode_jwt
from app.db.session import sessionLocal
from app.models.users import User

router = APIRouter(tags=["Chat WebSocket"])


@router.websocket("/ws/chat/{conversation_id}")
async def chat_socket(
    websocket: WebSocket,
    conversation_id: UUID,
):
    token = websocket.query_params.get("token")

    if token is None:
        await websocket.close(code=1008)
        return

    try:
        payload = decode_jwt(token)
    except Exception:
        await websocket.close(code=1008)
        return

    db = sessionLocal()

    try:
        user = db.get(User, payload["sub"])

        if user is None:
            await websocket.close(code=1008)
            return

        try:
            get_conversation(
                conversation_id=conversation_id,
                current_user=user,
                db=db,
            )
        except Exception:
            await websocket.close(code=1008)
            return

        await manager.connect(
            str(conversation_id),
            websocket,
        )

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(
            str(conversation_id),
            websocket,
        )

    finally:
        db.close()