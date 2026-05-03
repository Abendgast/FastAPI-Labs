from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status, Request

from lab7.auth import AuthStore, get_auth_store, get_current_user, login_and_issue_tokens
from lab7.schemas import BookCreate, BookRead, RefreshRequest, TokenPair
from lab7.storage import LibraryStore
from lab7.rate_limit import rate_limiter

app = FastAPI(title="Library API - Lab 7 (Rate Limiter)")

store = LibraryStore()

@app.get("/", summary="Healthcheck")
async def root(request: Request):
    await rate_limiter(request)
    return {"message": "ok", "docs": "/docs"}

@app.post("/auth/token", response_model=TokenPair, summary="Login: issue access+refresh tokens")
async def token(request: Request, payload=Depends(login_and_issue_tokens)):
    await rate_limiter(request)
    return payload

@app.post("/auth/refresh", response_model=TokenPair, summary="Refresh flow: rotate refresh token")
async def refresh_tokens(request: Request, req: RefreshRequest, auth: AuthStore = Depends(get_auth_store)):
    await rate_limiter(request)
    access, refresh = auth.rotate_refresh(refresh_token=req.refresh_token)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@app.get("/books", response_model=list[BookRead], summary="List books (protected)")
async def list_books(request: Request, _user=Depends(get_current_user)):
    await rate_limiter(request, user_id=_user["username"])
    return store.list_books()

@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED, summary="Create book (protected)")
async def create_book(request: Request, book_in: BookCreate, _user=Depends(get_current_user)):
    await rate_limiter(request, user_id=_user["username"])
    return store.create_book(
        title=book_in.title,
        author=book_in.author,
        year=book_in.year,
        description=book_in.description,
    )

@app.get("/books/{book_id}", response_model=BookRead, summary="Get book by id (protected)")
async def get_book(request: Request, book_id: str, _user=Depends(get_current_user)):
    await rate_limiter(request, user_id=_user["username"])
    doc = store.get_book(book_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return doc

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete book (protected)")
async def delete_book(request: Request, book_id: str, _user=Depends(get_current_user)):
    await rate_limiter(request, user_id=_user["username"])
    _ = store.delete_book(book_id)
    return None
