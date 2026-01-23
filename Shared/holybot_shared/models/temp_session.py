import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TempSession(Base):
    __tablename__ = "temp_session"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)

    username: Mapped[str]
    email: Mapped[str]
    verification_code_hash: Mapped[str]
    password_hash: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
