from app.core.enums import ListingStatus
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.listings import Listing
from app.models.users import User
from app.models.message import Message
from sqlalchemy import or_, update
from sqlalchemy.orm import joinedload


def create_or_get_conversation(
    listing_id: UUID,
    current_user: User,
    db: Session,
) -> Conversation:

    listing = db.get(Listing, listing_id)

    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot start a conversation on inactive listing.",
        )

    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot start a conversation on your own listing.",
        )

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.listing_id == listing.id,
            Conversation.buyer_id == current_user.id,
        )
        .first()
    )

    if conversation:
        return conversation

    conversation = Conversation(
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.seller_id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

def get_conversation(conversation_id, current_user, db):
    conversation = db.get(Conversation, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    if( conversation.buyer_id != current_user.id and conversation.seller_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation."
        )
    
    return conversation

def get_conversations(current_user: User, db: Session):
    conversations = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.listing).joinedload(Listing.images),
            joinedload(Conversation.buyer),
            joinedload(Conversation.seller),
        )
        .filter(
            or_(
                Conversation.buyer_id == current_user.id,
                Conversation.seller_id == current_user.id,
            )
        )
        .order_by(Conversation.last_message_at.desc())
        .all()
    )

    result = []

    for conversation in conversations:

        thumbnail = None 

        if conversation.listing.images:
            thumbnail = conversation.listing.images[0].file_key

        last_message = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation.id 
            )
            .order_by(Message.created_at.desc())
            .first()
        )

        unread_count = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation.id,
                Message.sender_id != current_user.id,
                Message.is_read == False,
            )
            .count()
        )

        other_user = (
            conversation.seller
            if conversation.buyer_id == current_user.id
            else conversation.buyer
        )

        result.append(
            {
                "id": conversation.id,
                "listing": {
                    "id": conversation.listing_id,
                    "title": conversation.listing.title,
                    "thumbnail": thumbnail
                },
                "other_user": other_user,
                "last_message": (
                    last_message.content if last_message else None
                ),
                "unread_count": unread_count,
                "last_message_at": conversation.last_message_at,
            }
        )

    return result

def send_message(conversation_id, content, current_user, db):
    content = content.strip()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    conversation = get_conversation(conversation_id,current_user,db)
    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        content=content,
    )

    db.add(message)
    conversation.last_message_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(message)

    return message

def get_messages(
    conversation_id,
    current_user,
    db: Session,
):
    conversation = get_conversation(
        conversation_id,
        current_user,
        db,
    )

    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

def mark_messages_read(conversation_id, current_user, db: Session):
    conversation = get_conversation(conversation_id,current_user,db)
    (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id,
            Message.sender_id != current_user.id,
            Message.is_read == False,
        )
        .update(
            {
                Message.is_read: True
            },
            synchronize_session=False,
        )
    )

    db.commit()

    return {"message": "Messages marked as read."}