from collections.abc import AsyncGenerator
import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "library")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "books")


client: AsyncIOMotorClient | None = None


async def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
    return client


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    _client = await get_client()
    db = _client[MONGO_DB_NAME]
    try:
        yield db
    finally:
        pass


async def get_books_collection() -> AsyncGenerator[AsyncIOMotorCollection, None]:
    async for db in get_db():
        yield db[MONGO_COLLECTION_NAME]

