import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Session(Base):
    __tablename__ = "session"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    refresh: Mapped[datetime.datetime]
    expires: Mapped[datetime.datetime]

    user: Mapped["User"] = relationship(back_populates="sessions")
