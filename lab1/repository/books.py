from typing import Dict, List, Optional
from uuid import UUID

from lab1.models.book import BOOKS_DB


async def list_books_repo() -> List[Dict]:
    return list(BOOKS_DB)


async def get_book_by_id_repo(book_id: UUID) -> Optional[Dict]:
    for book in BOOKS_DB:
        if str(book.get("id")) == str(book_id):
            return book
    return None


async def create_book_repo(book_data: Dict) -> Dict:
    BOOKS_DB.append(book_data)
    return book_data


async def delete_book_repo(book_id: UUID) -> None:
    # Ідемпотентне видалення: якщо книги немає, просто нічого не робимо.
    index_to_delete = None
    for idx, book in enumerate(BOOKS_DB):
        if str(book.get("id")) == str(book_id):
            index_to_delete = idx
            break

    if index_to_delete is not None:
        del BOOKS_DB[index_to_delete]

