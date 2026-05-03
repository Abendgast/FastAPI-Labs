from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from lab2.models.book import Book
from lab2.repository.books import (
    create_book_repo,
    delete_book_repo,
    get_book_by_id_repo,
    list_books_repo,
)
from lab2.schemas.book import (
    BookCreate,
    BookRead,
    BookStatus,
    PaginatedBooks,
    SortBy,
    SortOrder,
)

async def list_books_service(
    session: AsyncSession,
    *,
    status_filter: BookStatus | None,
    author_filter: str | None,
    sort_by: SortBy,
    sort_order: SortOrder,
    limit: int,
    offset: int,
) -> PaginatedBooks:
    items, total = await list_books_repo(
        session,
        status_filter=status_filter,
        author_filter=author_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return PaginatedBooks(
        items=[BookRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
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

