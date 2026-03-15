import os

from fastapi import FastAPI

from lab2.api.books import router as books_router
from lab2.db import init_db


app = FastAPI(title="Library API - Lab 2 (PostgreSQL)")


@app.on_event("startup")
async def on_startup() -> None:
    # Під час тестів використовуємо окремий in-memory SQLite
    # і не ініціалізуємо Postgres-підключення.
    if os.getenv("TESTING") == "1":
        return
    await init_db()


app.include_router(books_router, prefix="/books", tags=["books"])

