from fastapi import FastAPI

from lab1.api.books import router as books_router


app = FastAPI(title="Library API - Lab 1")


app.include_router(books_router, prefix="/books", tags=["books"])

