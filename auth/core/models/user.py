import enum
from datetime import datetime

from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func

from .base import Base


class SessionStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"


class User(Base):
    username: Mapped[str] = MappedColumn(
        String(22),
        nullable=False,
        unique=True,
    )
    hashed_password: Mapped[bytes] = MappedColumn(
        BYTEA,
        nullable=False,
    )


class Session(Base):
    uuid: Mapped[str] = MappedColumn()
    status: Mapped[SessionStatus] = MappedColumn(
        Enum(SessionStatus, name="session_status"), nullable=False
    )
    timestamp: Mapped[datetime] = MappedColumn(
        DateTime, server_default=func.current_timestamp()
    )
    sub: Mapped[str] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = MappedColumn(nullable=False)
    ip: Mapped[str] = MappedColumn(nullable=False)
    can_abort: Mapped[bool] = MappedColumn(nullable=False, default=False)
