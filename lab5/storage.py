from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

@dataclass
class LibraryStore:
    authors: dict[str, dict[str, Any]] = field(default_factory=dict)
    books: dict[str, dict[str, Any]] = field(default_factory=dict)

    def create_author(self, name: str) -> dict[str, Any]:
        author_id = uuid4().hex
        doc = {"id": author_id, "name": name}
        self.authors[author_id] = doc
        return doc

    def list_authors(self) -> list[dict[str, Any]]:
        return sorted(self.authors.values(), key=lambda x: x["name"])

    def get_author(self, author_id: str) -> dict[str, Any] | None:
        return self.authors.get(author_id)

    def update_author(self, author_id: str, name: str) -> dict[str, Any] | None:
        existing = self.authors.get(author_id)
        if not existing:
            return None
        existing["name"] = name
        return existing

    def delete_author(self, author_id: str) -> bool:
        if author_id not in self.authors:
            return False
        self.authors.pop(author_id, None)
        for book_id, book in list(self.books.items()):
            if book["author_id"] == author_id:
                self.books.pop(book_id, None)
        return True

    def create_book(self, title: str, author_id: str, year: int | None, tags: list[str]) -> dict[str, Any] | None:
        if author_id not in self.authors:
            return None
        book_id = uuid4().hex
        doc = {"id": book_id, "title": title, "author_id": author_id, "year": year, "tags": tags}
        self.books[book_id] = doc
        return doc

    def list_books(self) -> list[dict[str, Any]]:
        return sorted(self.books.values(), key=lambda x: x["title"])

    def get_book(self, book_id: str) -> dict[str, Any] | None:
        return self.books.get(book_id)

    def update_book(
        self,
        book_id: str,
        title: str | None,
        author_id: str | None,
        year: int | None,
        tags: list[str] | None,
    ) -> dict[str, Any] | None:
        existing = self.books.get(book_id)
        if not existing:
            return None
        if author_id is not None and author_id not in self.authors:
            return None
        if title is not None:
            existing["title"] = title
        if author_id is not None:
            existing["author_id"] = author_id
        existing["year"] = year
        if tags is not None:
            existing["tags"] = tags
        return existing

    def delete_book(self, book_id: str) -> bool:
        if book_id not in self.books:
            return False
        self.books.pop(book_id, None)
        return True
