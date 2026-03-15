from typing import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lab3.models.book import Book
from lab3.schemas.book import BookStatus, SortBy, SortOrder


async def list_books_repo(
    session: AsyncSession,
    *,
    status_filter: BookStatus | None,
    author_filter: str | None,
    sort_by: SortBy,
    sort_order: SortOrder,
    limit: int,
    offset: int,
) -> Sequence[Book]:
    stmt: Select = select(Book)

    if status_filter is not None:
        stmt = stmt.where(Book.status == status_filter)

    if author_filter:
        pattern = f"%{author_filter.lower()}%"
        stmt = stmt.where(func.lower(Book.author).like(pattern))

    if sort_by == SortBy.title:
        order_col = func.lower(Book.title)
    else:
        order_col = Book.year

    if sort_order == SortOrder.desc:
        order_col = order_col.desc()

    # Беремо на один запис більше, щоб визначити наявність наступної сторінки
    stmt = stmt.order_by(order_col).limit(limit + 1).offset(offset)

    result = await session.execute(stmt)
    items = result.scalars().all()

    return items


async def get_book_by_id_repo(session: AsyncSession, book_id: str) -> Book | None:
    return await session.get(Book, book_id)


async def create_book_repo(session: AsyncSession, book: Book) -> Book:
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


async def delete_book_repo(session: AsyncSession, book_id: str) -> None:
    book = await session.get(Book, book_id)
    if book is None:
        return
    await session.delete(book)
    await session.commit()

