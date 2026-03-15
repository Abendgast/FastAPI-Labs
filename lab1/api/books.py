from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from lab1.schemas.book import BookCreate, BookRead, BookStatus, SortBy, SortOrder
from lab1.services.books import (
    create_book_service,
    delete_book_service,
    get_book_by_id_service,
    list_books_service,
)


router = APIRouter()


@router.get(
    "",
    response_model=List[BookRead],
    status_code=status.HTTP_200_OK,
    summary="Отримати список книг",
)
async def get_books(
    status_filter: Optional[BookStatus] = Query(
        default=None, alias="status", description="Фільтр по статусу книги"
    ),
    author: Optional[str] = Query(
        default=None, description="Фільтр по автору (повний або частковий збіг)"
    ),
    sort_by: SortBy = Query(
        default=SortBy.title, description="Поле сортування: назва або рік випуску"
    ),
    sort_order: SortOrder = Query(
        default=SortOrder.asc, description="Порядок сортування: за зростанням або спаданням"
    ),
):
    return await list_books_service(
        status_filter=status_filter,
        author_filter=author,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{book_id}",
    response_model=BookRead,
    status_code=status.HTTP_200_OK,
    summary="Отримати книгу за ID",
)
async def get_book_by_id(book_id: UUID):
    book = await get_book_by_id_service(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книгу не знайдено"
        )
    return book


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    summary="Додати нову книгу",
)
async def create_book(book_in: BookCreate):
    return await create_book_service(book_in)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити книгу (ідемпотентно)",
)
async def delete_book(book_id: UUID):
    await delete_book_service(book_id)
    # Ідемпотентність: завжди повертаємо 204, навіть якщо книги не існувало
    return None

