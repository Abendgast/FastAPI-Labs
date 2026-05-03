from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorCollection

from lab4.db import get_books_collection
from lab4.schemas.book import (
    BookCreate,
    BookRead,
    BookStatus,
    PaginatedBooks,
    SortBy,
    SortOrder,
)
from lab4.services.books import (
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
    summary="Отримати список книг (Mongo, Limit-Offset пагінація)",
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
    collection: AsyncIOMotorCollection = Depends(get_books_collection),
):
    return await list_books_service(
        collection,
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
async def get_book_by_id(
    book_id: str, collection: AsyncIOMotorCollection = Depends(get_books_collection)
):
    book = await get_book_by_id_service(collection, book_id)
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
    book_in: BookCreate, collection: AsyncIOMotorCollection = Depends(get_books_collection)
):
    return await create_book_service(collection, book_in)

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити книгу (ідемпотентно)",
)
async def delete_book(
    book_id: str, collection: AsyncIOMotorCollection = Depends(get_books_collection)
):
    await delete_book_service(collection, book_id)
    return None

