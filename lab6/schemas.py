from __future__ import annotations

from pydantic import BaseModel, Field, constr


TitleStr = constr(min_length=1, max_length=255, strip_whitespace=True)
AuthorStr = constr(min_length=1, max_length=255, strip_whitespace=True)
DescriptionStr = constr(min_length=0, max_length=2000, strip_whitespace=True)


class BookCreate(BaseModel):
    title: TitleStr
    author: AuthorStr
    year: int = Field(..., ge=0, le=2100)
    description: DescriptionStr | None = None


class BookRead(BookCreate):
    id: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str

