from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    token = Column(
        String(512),
        unique=True,
        index=True,
        nullable=False,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )