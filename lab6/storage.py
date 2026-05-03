from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

@dataclass
class LibraryStore:
    books: dict[str, dict[str, Any]] = field(default_factory=dict)

    def create_book(self, *, title: str, author: str, year: int, description: str | None) -> dict[str, Any]:
        book_id = uuid4().hex
        doc = {
            "id": book_id,
            "title": title,
            "author": author,
            "year": year,
            "description": description,
        }
        self.books[book_id] = doc
        return doc

    def list_books(self) -> list[dict[str, Any]]:
        return sorted(self.books.values(), key=lambda x: x["title"])

    def get_book(self, book_id: str) -> dict[str, Any] | None:
        return self.books.get(book_id)

    def delete_book(self, book_id: str) -> bool:
        if book_id not in self.books:
            return False
        self.books.pop(book_id, None)
        return True

