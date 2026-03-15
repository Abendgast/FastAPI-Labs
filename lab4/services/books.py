from motor.motor_asyncio import AsyncIOMotorCollection

from lab4.repository.books import (
    create_book_repo,
    delete_book_repo,
    get_book_by_id_repo,
    list_books_repo,
)
from lab4.schemas.book import (
    BookCreate,
    BookRead,
    BookStatus,
    PaginatedBooks,
    SortBy,
    SortOrder,
)


async def list_books_service(
    collection: AsyncIOMotorCollection,
    *,
    status_filter: BookStatus | None,
    author_filter: str | None,
    sort_by: SortBy,
    sort_order: SortOrder,
    limit: int,
    offset: int,
) -> PaginatedBooks:
    items, total = await list_books_repo(
        collection,
        status_filter=status_filter,
        author_filter=author_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return PaginatedBooks(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_book_by_id_service(
    collection: AsyncIOMotorCollection, book_id: str
) -> BookRead | None:
    return await get_book_by_id_repo(collection, book_id)


async def create_book_service(
    collection: AsyncIOMotorCollection, book_in: BookCreate
) -> BookRead:
    return await create_book_repo(collection, book_in)


async def delete_book_service(
    collection: AsyncIOMotorCollection, book_id: str
) -> None:
    await delete_book_repo(collection, book_id)

