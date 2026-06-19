from sqlalchemy import String, UUID as SA_UUID, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
import uuid
from app.db.base import Base
from app.db.mixins import TimestampMixin

class ListingImage(TimestampMixin, Base):
    __tablename__ = "listing_images"
    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        primary_key = True,
        default = uuid.uuid4
    )

    listing_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        ForeignKey("listings.id"),
        nullable = False
    )

    file_key: Mapped[str] = mapped_column(
        String(500),
        nullable = False
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        default = 0
    )

    listing = relationship("Listing", back_populates="images")