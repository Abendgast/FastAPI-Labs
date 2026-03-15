from fastapi import FastAPI

from lab4.api.books import router as books_router


app = FastAPI(title="Library API - Lab 4 (MongoDB)")


app.include_router(books_router, prefix="/books", tags=["books"])

