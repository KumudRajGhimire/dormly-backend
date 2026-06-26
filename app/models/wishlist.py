from sqlalchemy import UniqueConstraint
from uuid import UUID
import uuid

from sqlalchemy import UUID as SA_UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.users import User
from app.models.listings import Listing

from app.db.mixins import TimestampMixin
from app.db.base import Base


class Wishlist(Base, TimestampMixin):
    __tablename__ = "wishlists"

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        primary_key = True,
        default = uuid.uuid4 
    )

    user_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        ForeignKey("users.id"),
        nullable = False
    )

    listing_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        ForeignKey("listings.id"),
        nullable = False
    )

    user: Mapped["User"] = relationship(
        back_populates = "wishlists"
    )

    listing: Mapped["Listing"] = relationship(
        back_populates = "wishlists"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_listing_wishlist"),
    )
