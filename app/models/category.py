from sqlalchemy.orm import relationship
import uuid
from uuid import UUID

from sqlalchemy import String, UUID as SA_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin

class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        primary_key = True,
        default = uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique = True,
        nullable = False
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique = True,
        nullable = False
    )

    icon: Mapped[str|None] = mapped_column(
        String(255),
        nullable = True
    )

    listings = relationship("Listing", back_populates = "category")