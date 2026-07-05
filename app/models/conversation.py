import uuid
from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, UUID as SA_UUID, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin
from sqlalchemy import UniqueConstraint

class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    listing_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("listings.id"),
        nullable=False,
    )

    buyer_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    seller_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    listing = relationship(
        "Listing",
        back_populates="conversations",
    )

    buyer = relationship(
        "User",
        foreign_keys=[buyer_id],
        back_populates="buyer_conversations",
    )

    seller = relationship(
        "User",
        foreign_keys=[seller_id],
        back_populates="seller_conversations",
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "listing_id",
            "buyer_id",
            name="uq_listing_buyer_conversation",
        ),
    )