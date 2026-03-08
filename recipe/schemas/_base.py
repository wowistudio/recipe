"""Base models for the application."""

from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID as TUUID

from sqlalchemy import UUID, DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now_naive() -> datetime:
    """Current datetime in UTC as naive datetime (no timezone info)."""
    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    """Base class for all models."""

    id: Mapped[TUUID] = mapped_column(
        UUID, primary_key=True, server_default=text("uuid_generate_v4()")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now_naive, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now_naive, onupdate=utc_now_naive, nullable=False
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        # only keys that are in the model are allowed
        allowed_keys = cls.__table__.columns.keys()
        return cls(**{k: v for k, v in data.items() if k in allowed_keys})
