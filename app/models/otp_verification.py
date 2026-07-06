import uuid
from uuid import UUID
from datetime import datetime

from sqlalchemy import (
    String,
    UUID as SA_UUID,
    Enum,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base
from app.db.mixins import TimestampMixin
from app.core.enums import OTPPurpose


class OTPVerification(TimestampMixin, Base):
    __tablename__ = "otp_verifications"

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    otp_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    purpose: Mapped[OTPPurpose] = mapped_column(
        Enum(OTPPurpose),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )