from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr

class BookStatus(str, Enum):
    available = "available"
    issued = "issued"

class SortBy(str, Enum):
    title = "title"
    year = "year"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

TitleStr = constr(min_length=1, max_length=255, strip_whitespace=True)
AuthorStr = constr(min_length=1, max_length=255, strip_whitespace=True)
DescriptionStr = constr(min_length=0, max_length=2000, strip_whitespace=True)

class BookBase(BaseModel):
    title: TitleStr = Field(..., description="Назва книги")
    author: AuthorStr = Field(..., description="Автор книги")
    description: Optional[DescriptionStr] = Field(
        default=None, description="Опис книги"
    )
    status: BookStatus = Field(
        default=BookStatus.available, description="Статус книги у бібліотеці"
    )
    year: int = Field(..., ge=0, le=2100, description="Рік випуску книги")

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    id: UUID = Field(..., description="Унікальний ідентифікатор книги")

    class Config:
        from_attributes = True

class CursorPaginatedBooks(BaseModel):
    items: list[BookRead]
    limit: int = Field(..., description="Кількість елементів на сторінці")
    next_cursor: Optional[str] = Field(
        default=None,
        description=(
            "Курсор для наступної сторінки. "
            "Якщо None, наступної сторінки немає."
        ),
    )

