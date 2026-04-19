from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status

from lab6.auth import AuthStore, get_auth_store, get_current_user, login_and_issue_tokens
from lab6.schemas import BookCreate, BookRead, RefreshRequest, TokenPair
from lab6.storage import LibraryStore


app = FastAPI(title="Library API - Lab 6 (JWT access/refresh)")

store = LibraryStore()


@app.get("/", summary="Healthcheck")
def root():
    return {"message": "ok", "docs": "/docs"}


@app.post("/auth/token", response_model=TokenPair, summary="Login: issue access+refresh tokens")
def token(payload=Depends(login_and_issue_tokens)):
    return payload


@app.post("/auth/refresh", response_model=TokenPair, summary="Refresh flow: rotate refresh token")
def refresh_tokens(req: RefreshRequest, auth: AuthStore = Depends(get_auth_store)):
    access, refresh = auth.rotate_refresh(refresh_token=req.refresh_token)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@app.get("/books", response_model=list[BookRead], summary="List books (protected)")
def list_books(_user=Depends(get_current_user)):
    return store.list_books()


@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED, summary="Create book (protected)")
def create_book(book_in: BookCreate, _user=Depends(get_current_user)):
    return store.create_book(
        title=book_in.title,
        author=book_in.author,
        year=book_in.year,
        description=book_in.description,
    )


@app.get("/books/{book_id}", response_model=BookRead, summary="Get book by id (protected)")
def get_book(book_id: str, _user=Depends(get_current_user)):
    doc = store.get_book(book_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return doc


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete book (protected)")
def delete_book(book_id: str, _user=Depends(get_current_user)):
    _ = store.delete_book(book_id)
    return None

