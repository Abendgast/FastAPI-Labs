from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from lab2.db import get_session
from lab2.schemas.book import (
    BookCreate,
    BookRead,
    BookStatus,
    PaginatedBooks,
    SortBy,
    SortOrder,
)
from lab2.services.books import (
    create_book_service,
    delete_book_service,
    get_book_by_id_service,
    list_books_service,
)

router = APIRouter()

@router.get(
    "",
    response_model=PaginatedBooks,
    status_code=status.HTTP_200_OK,
    summary="Отримати список книг (з пагінацією)",
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
        default=SortOrder.asc,
        description="Порядок сортування: за зростанням або спаданням",
    ),
    limit: int = Query(
        default=10, ge=1, le=100, description="Кількість елементів на сторінці"
    ),
    offset: int = Query(
        default=0, ge=0, description="Зміщення (offset) для пагінації"
    ),
    session: AsyncSession = Depends(get_session),
):
    return await list_books_service(
        session,
        status_filter=status_filter,
        author_filter=author,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/{book_id}",
    response_model=BookRead,
    status_code=status.HTTP_200_OK,
    summary="Отримати книгу за ID",
)
async def get_book_by_id(book_id: str, session: AsyncSession = Depends(get_session)):
    book = await get_book_by_id_service(session, book_id)
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
async def create_book(
    book_in: BookCreate, session: AsyncSession = Depends(get_session)
):
    return await create_book_service(session, book_in)

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити книгу (ідемпотентно)",
)
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session)):
    await delete_book_service(session, book_id)
    return None

