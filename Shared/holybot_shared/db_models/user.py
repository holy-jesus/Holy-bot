from typing import TYPE_CHECKING
from uuid import uuid7, UUID
import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .session import Session
    from .twitch_token import TwitchToken


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid7)
    email: Mapped[str]
    username: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)

    password_hash: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), server_onupdate=func.now())

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    twitch_token: Mapped["TwitchToken"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
