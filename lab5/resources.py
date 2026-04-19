from __future__ import annotations

from flask import request
from flask_restful import Resource
from flasgger import swag_from

from storage import LibraryStore


def _json() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _err(message: str, code: int):
    return {"message": message}, code


class AuthorListResource(Resource):
    def __init__(self, store: LibraryStore):
        self.store = store

    @swag_from("docs/authors_list_get.yml")
    def get(self):
        return self.store.list_authors(), 200

    @swag_from("docs/authors_list_post.yml")
    def post(self):
        payload = _json()
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            return _err("Validation error", 400)
        doc = self.store.create_author(name=name.strip())
        return doc, 201


class AuthorResource(Resource):
    def __init__(self, store: LibraryStore):
        self.store = store

    @swag_from("docs/authors_get.yml")
    def get(self, author_id: str):
        doc = self.store.get_author(author_id)
        if not doc:
            return _err("Not found", 404)
        return doc, 200

    @swag_from("docs/authors_put.yml")
    def put(self, author_id: str):
        payload = _json()
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            return _err("Validation error", 400)
        updated = self.store.update_author(author_id, name.strip())
        if not updated:
            return _err("Not found", 404)
        return updated, 200

    @swag_from("docs/authors_delete.yml")
    def delete(self, author_id: str):
        ok = self.store.delete_author(author_id)
        if not ok:
            return _err("Not found", 404)
        return {"status": "deleted"}, 200


class BookListResource(Resource):
    def __init__(self, store: LibraryStore):
        self.store = store

    @swag_from("docs/books_list_get.yml")
    def get(self):
        return self.store.list_books(), 200

    @swag_from("docs/books_list_post.yml")
    def post(self):
        payload = _json()
        title = payload.get("title")
        author_id = payload.get("author_id")
        year = payload.get("year")
        tags = payload.get("tags", [])
        if not isinstance(title, str) or not title.strip():
            return _err("Validation error", 400)
        if not isinstance(author_id, str) or not author_id.strip():
            return _err("Validation error", 400)
        if year is not None and not isinstance(year, int):
            return _err("Validation error", 400)
        if not isinstance(tags, list) or not all(isinstance(x, str) for x in tags):
            return _err("Validation error", 400)
        created = self.store.create_book(title.strip(), author_id.strip(), year, tags)
        if not created:
            return _err("Validation error", 400)
        return created, 201


class BookResource(Resource):
    def __init__(self, store: LibraryStore):
        self.store = store

    @swag_from("docs/books_get.yml")
    def get(self, book_id: str):
        doc = self.store.get_book(book_id)
        if not doc:
            return _err("Not found", 404)
        return doc, 200

    @swag_from("docs/books_put.yml")
    def put(self, book_id: str):
        payload = _json()
        title = payload.get("title")
        author_id = payload.get("author_id")
        year = payload.get("year")
        tags = payload.get("tags")
        if title is not None and (not isinstance(title, str) or not title.strip()):
            return _err("Validation error", 400)
        if author_id is not None and (not isinstance(author_id, str) or not author_id.strip()):
            return _err("Validation error", 400)
        if year is not None and not isinstance(year, int):
            return _err("Validation error", 400)
        if tags is not None and (not isinstance(tags, list) or not all(isinstance(x, str) for x in tags)):
            return _err("Validation error", 400)
        updated = self.store.update_book(
            book_id=book_id,
            title=title.strip() if isinstance(title, str) else None,
            author_id=author_id.strip() if isinstance(author_id, str) else None,
            year=year if isinstance(year, int) or year is None else None,
            tags=tags,
        )
        if not updated:
            existing = self.store.get_book(book_id)
            return _err("Not found", 404) if not existing else _err("Validation error", 400)
        return updated, 200

    @swag_from("docs/books_delete.yml")
    def delete(self, book_id: str):
        ok = self.store.delete_book(book_id)
        if not ok:
            return _err("Not found", 404)
        return {"status": "deleted"}, 200

