import base64
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from lab3.models.book import Book
from lab3.repository.books import (
    create_book_repo,
    delete_book_repo,
    get_book_by_id_repo,
    list_books_repo,
)
from lab3.schemas.book import (
    BookCreate,
    BookRead,
    BookStatus,
    CursorPaginatedBooks,
    SortBy,
    SortOrder,
)


def encode_cursor(offset: int) -> str:
    raw = str(offset).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_cursor(cursor: str) -> int:
    raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
    offset = int(raw)
    if offset < 0:
        raise ValueError("Offset must be non-negative")
    return offset


async def list_books_service(
    session: AsyncSession,
    *,
    status_filter: BookStatus | None,
    author_filter: str | None,
    sort_by: SortBy,
    sort_order: SortOrder,
    limit: int,
    cursor: str | None,
) -> CursorPaginatedBooks:
    if cursor is None:
        offset = 0
    else:
        offset = decode_cursor(cursor)

    # Репозиторій повертає до limit + 1 записів
    raw_items = await list_books_repo(
        session,
        status_filter=status_filter,
        author_filter=author_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    has_next = len(raw_items) > limit
    items = raw_items[:limit]

    next_cursor = None
    if has_next:
        next_offset = offset + limit
        next_cursor = encode_cursor(next_offset)

    return CursorPaginatedBooks(
        items=[BookRead.model_validate(item) for item in items],
        limit=limit,
        next_cursor=next_cursor,
    )


async def get_book_by_id_service(
    session: AsyncSession, book_id: str
) -> BookRead | None:
    book = await get_book_by_id_repo(session, book_id)
    if not book:
        return None
    return BookRead.model_validate(book)


async def create_book_service(
    session: AsyncSession, book_in: BookCreate
) -> BookRead:
    book = Book(
        id=str(uuid4()),
        title=book_in.title,
        author=book_in.author,
        description=book_in.description,
        status=book_in.status,
        year=book_in.year,
    )
    book = await create_book_repo(session, book)
    return BookRead.model_validate(book)


async def delete_book_service(session: AsyncSession, book_id: str) -> None:
    await delete_book_repo(session, book_id)

