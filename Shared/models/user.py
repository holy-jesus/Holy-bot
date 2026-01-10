import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .session import Session


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str]
    username: Mapped[str]

    password_hash: Mapped[str]

    created_at: Mapped[datetime.datetime]
    updated_at: Mapped[datetime.datetime]
    last_login_at: Mapped[datetime.datetime]

    sessions: Mapped[List["Session"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    # twitch_authentication
