import datetime
from typing import TYPE_CHECKING
from uuid import uuid7, UUID

from sqlalchemy import JSON, func, ForeignKey
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
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), server_onupdate=func.now())

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(
        back_populates="twitch_token"
    )
