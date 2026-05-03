import os

from fastapi import FastAPI

from lab3.api.books import router as books_router
from lab3.db import init_db

app = FastAPI(title="Library API - Lab 3 (PostgreSQL, Cursor pagination)")

@app.on_event("startup")
async def on_startup() -> None:
    if os.getenv("TESTING") == "1":
        return
    await init_db()

app.include_router(books_router, prefix="/books", tags=["books"])

