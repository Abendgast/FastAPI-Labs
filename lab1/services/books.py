from typing import Dict, List, Optional

from lab1.repository.books import (
    create_book_repo,
    delete_book_repo,
    get_book_by_id_repo,
    list_books_repo,
)
from lab1.schemas.book import BookCreate, BookRead, BookStatus, SortBy, SortOrder


async def list_books_service(
    status_filter: Optional[BookStatus],
    author_filter: Optional[str],
    sort_by: SortBy,
    sort_order: SortOrder,
) -> List[BookRead]:
    books_raw: List[Dict] = await list_books_repo()

    # Фільтрація по статусу
    if status_filter is not None:
        books_raw = [
            b for b in books_raw if b.get("status") == status_filter.value
        ]

    # Фільтрація по автору (частковий, case-insensitive)
    if author_filter:
        author_lower = author_filter.lower()
        books_raw = [
            b
            for b in books_raw
            if author_lower in str(b.get("author", "")).lower()
        ]

    reverse = sort_order == SortOrder.desc
    if sort_by == SortBy.title:
        books_raw.sort(key=lambda b: str(b.get("title", "")).lower(), reverse=reverse)
    elif sort_by == SortBy.year:
        books_raw.sort(key=lambda b: int(b.get("year", 0)), reverse=reverse)

    # Серіалізація у Pydantic-схему
    return [BookRead(**book) for book in books_raw]


async def get_book_by_id_service(book_id) -> Optional[BookRead]:
    book_raw = await get_book_by_id_repo(book_id)
    if not book_raw:
        return None
    return BookRead(**book_raw)


async def create_book_service(book_in: BookCreate) -> BookRead:
    # Створюємо Pydantic-об'єкт BookRead (генерує UUID)
    book = BookRead(**book_in.dict())
    await create_book_repo(book.dict())
    return book


async def delete_book_service(book_id) -> None:
    await delete_book_repo(book_id)

