from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Text, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from lab3.db import Base
from lab3.schemas.book import BookStatus

class Book(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[BookStatus] = mapped_column(
        SAEnum(BookStatus, name="book_status"),
        nullable=False,
        default=BookStatus.available,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)

