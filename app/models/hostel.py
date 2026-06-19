from sqlalchemy.orm import relationship
import uuid
from uuid import UUID

from sqlalchemy import String, UUID as SA_UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin

class Hostel(TimestampMixin, Base):
    __tablename__ = "hostels"

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4
    )

    campus_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        ForeignKey("campuses.id"),
        nullable = False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable = False
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable = False
    )

    campus = relationship("Campus", back_populates = "hostels")