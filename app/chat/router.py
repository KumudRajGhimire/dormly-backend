from app.chat.service import mark_messages_read
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.chat.websocket import manager

from app.auth.dependencies import get_current_user
from app.chat.service import create_or_get_conversation,send_message, get_conversations, get_messages
from app.db.session import get_db
from app.models.users import User
from app.schemas.chat import ConversationResponse, MessageCreate, MessageResponse, ConversationListResponse, MessageResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/listings/{listing_id}/conversation",response_model=ConversationResponse)
def open_conversation(listing_id: UUID,current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):
    return create_or_get_conversation(
        listing_id,
        current_user,
        db,
    )

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(conversation_id: UUID, payload: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    message = send_message(
        conversation_id = conversation_id,
        content = payload.content,
        current_user = current_user,
        db = db
    )
    await manager.broadcast(
        str(conversation_id),
        {
            "type": "message",
            "id": str(message.id),
            "conversation_id": str(conversation_id),
            "sender_id": str(message.sender_id),
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        },
    )
    return message

@router.get("/conversations", response_model=list[ConversationListResponse])
def list_conversations(current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):
    return get_conversations(current_user=current_user,db=db)

@router.get("/conversations/{conversation_id}/messages",response_model=list[MessageResponse])
def list_messages(conversation_id: UUID,current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):
    return get_messages(conversation_id=conversation_id,current_user=current_user,db=db)

@router.patch("/conversations/{conversation_id}/read")
def read_messages(conversation_id: UUID, current_user:User = Depends(get_current_user),db: Session = Depends(get_db),):
    return mark_messages_read(conversation_id,current_user,db)