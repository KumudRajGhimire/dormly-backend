from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserResponse
from app.schemas.listing import ListingImageResponse


class ConversationResponse(BaseModel):
    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    last_message_at: datetime

    model_config = {
        "from_attributes": True
    }


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    content: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class ConversationListing(BaseModel):
    id: UUID
    title: str
    thumbnail: str|None

    model_config = {
        "from_attributes": True
    }


class ConversationUser(BaseModel):
    id: UUID
    username: str
    name: str

    model_config = {
        "from_attributes": True
    }


class ConversationListResponse(BaseModel):
    id: UUID

    listing: ConversationListing

    other_user: ConversationUser

    last_message: str | None 

    unread_count: int

    last_message_at: datetime

    model_config = {
        "from_attributes": True
    }