import uuid
from uuid import UUID

from sqlalchemy import String, UUID as SA_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

class Campus(TimestampMixin, Base):
    __tablename__ = "campuses"
    
    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable = False,
        unique = True
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique = True,
        nullable = False  
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable = False 
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable = False
    )

    email_domain: Mapped[str] = mapped_column(
        String(100),
        unique = True,
        nullable = False
    )

    hostels = relationship("Hostel", back_populates = "campus")
    users = relationship("User", back_populates = "campus")