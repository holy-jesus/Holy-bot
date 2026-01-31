from typing import TYPE_CHECKING
from uuid import uuid7, UUID
import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .session import Session
    from .twitch_token import TwitchToken


class TwitchChannel(Base):
    __tablename__ = "twitch_channel"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=str)

    email: Mapped[str]
    login: Mapped[str]
    username: Mapped[str]

    title: Mapped[str]
    category: Mapped[str]
    is_streaming: Mapped[bool]
    

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), server_onupdate=func.now()
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="twitch_channel")
