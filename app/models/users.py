from sqlalchemy import String, UUID as SA_UUID, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
import uuid
from app.db.mixins import TimestampMixin
from app.core.enums import UserRole
from app.db.base import Base

class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
        default = uuid.uuid4
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique = True,
        nullable = False
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable = False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique = True,
        nullable = False
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255)
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default = UserRole.USER,
        nullable = False
    )

    campus_id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid = True),
        ForeignKey("campuses.id"),
        nullable = False
    )
    
    hostel_id: Mapped[UUID|None] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("hostels.id"),
        nullable = True
    )


    listings = relationship("Listing", back_populates = "seller")
    campus = relationship("Campus", back_populates = "users")
    hostel = relationship("Hostel", back_populates = "users")
    wishlists = relationship("Wishlist", back_populates = "user", cascade = "all, delete-orphan")
