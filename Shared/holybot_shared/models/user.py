from typing import TYPE_CHECKING
from uuid import uuid7
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID

from .base import Base

if TYPE_CHECKING:
    from .session import Session
    from .twitch_token import TwitchToken


class User(Base):
    __tablename__ = "user"

    # id: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid7)
    email: Mapped[str]
    username: Mapped[str]

    password_hash: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime.datetime]
    updated_at: Mapped[datetime.datetime]
    last_login_at: Mapped[datetime.datetime]

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    twitch_token: Mapped["TwitchToken"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
