from typing import Sequence

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic_mongo import PydanticObjectId

from lab4.schemas.book import BookCreate, BookRead, BookStatus, SortBy, SortOrder

async def create_book_repo(
    collection: AsyncIOMotorCollection, book_in: BookCreate
) -> BookRead:
    doc = book_in.model_dump()
    result = await collection.insert_one(doc)
    created = await collection.find_one({"_id": result.inserted_id})
    return _mongo_to_book_read(created)

async def get_book_by_id_repo(
    collection: AsyncIOMotorCollection, book_id: str
) -> BookRead | None:
    oid = PydanticObjectId(book_id)
    doc = await collection.find_one({"_id": oid})
    if not doc:
        return None
    return _mongo_to_book_read(doc)

async def delete_book_repo(
    collection: AsyncIOMotorCollection, book_id: str
) -> None:
    oid = PydanticObjectId(book_id)
    response = await collection.delete_one({"_id": oid})
    _ = response.deleted_count

async def list_books_repo(
    collection: AsyncIOMotorCollection,
    *,
    status_filter: BookStatus | None,
    author_filter: str | None,
    sort_by: SortBy,
    sort_order: SortOrder,
    limit: int,
    offset: int,
) -> tuple[Sequence[BookRead], int]:
    query: dict = {}
    if status_filter is not None:
        query["status"] = status_filter.value

    if author_filter:
        query["author"] = {"$regex": author_filter, "$options": "i"}

    if sort_by == SortBy.title:
        sort_field = "title"
    else:
        sort_field = "year"
    sort_direction = 1 if sort_order == SortOrder.asc else -1
    cursor = collection.find(query).sort(sort_field, sort_direction).skip(offset).limit(
        limit
    )

    docs: list[dict] = []
    async for doc in cursor:
        docs.append(doc)
    total = await collection.count_documents(query)

    items = [_mongo_to_book_read(doc) for doc in docs]
    return items, int(total)

def _mongo_to_book_read(doc: dict) -> BookRead:
    return BookRead(
        id=PydanticObjectId(doc["_id"]),
        title=doc["title"],
        author=doc["author"],
        description=doc.get("description"),
        status=BookStatus(doc["status"]),
        year=doc["year"],
    )

