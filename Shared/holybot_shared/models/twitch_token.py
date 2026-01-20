import datetime
from typing import TYPE_CHECKING, List
from uuid import uuid7

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class TwitchToken(Base):
    __tablename__ = "twitch_token"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False, default=uuid7)

    encrypted_token: Mapped[str]
    encrypted_refresh_token: Mapped[str]
    expires_at: Mapped[datetime.datetime]
    scopes: Mapped[List[str]]

    created_at: Mapped[datetime.datetime]
    updated_at: Mapped[datetime.datetime]

    user: Mapped["User"] = relationship(
        back_populates="twitch_token"
    )
