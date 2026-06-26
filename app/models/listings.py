from sqlalchemy import String, UUID as SA_UUID, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
import uuid
from app.db.mixins import TimestampMixin
from app.db.base import Base
from app.core.enums import ListingStatus, ListingCondition

class Listing(TimestampMixin, Base):
    __tablename__ = "listings"
    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable = False 
    )
    description: Mapped[Text] = mapped_column(
        Text,
        nullable = False
    )
    price: Mapped[int] = mapped_column(
        Integer,
        nullable = False
    )
    seller_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable = False
    )

    condition: Mapped[ListingCondition] = mapped_column(
        Enum(ListingCondition),
        default = ListingCondition.GOOD,
        nullable = False
    )

    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus),
        default = ListingStatus.ACTIVE,
        nullable = False
    )

    category_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        ForeignKey("categories.id"),
        nullable = False
    )


    seller = relationship("User", back_populates="listings")
    images = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan")
    category = relationship("Category", back_populates="listings")
    wishlists = relationship("Wishlist", back_populates="listing", cascade="all, delete-orphan")
    


    