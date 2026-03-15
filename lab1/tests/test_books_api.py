from typing import List
from uuid import UUID

from fastapi.testclient import TestClient

from lab1.main import app
from lab1.models.book import BOOKS_DB


client = TestClient(app)


def setup_function():
    # Очищаємо in-memory базу перед кожним тестом
    BOOKS_DB.clear()


def _create_sample_books(count: int = 3) -> List[dict]:
    books = []
    for i in range(count):
        response = client.post(
            "/books",
            json={
                "title": f"Book {i}",
                "author": f"Author {i % 2}",
                "description": f"Desc {i}",
                "status": "available" if i % 2 == 0 else "issued",
                "year": 2000 + i,
            },
        )
        assert response.status_code == 201
        books.append(response.json())
    return books


def test_create_book_success():
    response = client.post(
        "/books",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "description": "Some description",
            "status": "available",
            "year": 2020,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["status"] == "available"
    assert data["year"] == 2020
    # Перевірка UUID
    UUID(data["id"])


def test_create_book_validation_error():
    # Немає обов'язкового поля title
    response = client.post(
        "/books",
        json={
            "author": "Test Author",
            "year": -1,  # некоректний рік
        },
    )
    assert response.status_code == 422


def test_get_all_books_basic():
    _create_sample_books(3)
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_books_filter_by_status():
    _create_sample_books(4)
    response = client.get("/books", params={"status": "available"})
    assert response.status_code == 200
    data = response.json()
    assert all(book["status"] == "available" for book in data)


def test_get_books_filter_by_author_partial():
    _create_sample_books(3)
    response = client.get("/books", params={"author": "author 1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all("author 1".lower() in book["author"].lower() for book in data)


def test_get_books_sort_by_title_desc():
    _create_sample_books(3)
    response = client.get("/books", params={"sort_by": "title", "sort_order": "desc"})
    assert response.status_code == 200
    data = response.json()
    titles = [b["title"] for b in data]
    assert titles == sorted(titles, key=lambda x: x.lower(), reverse=True)


def test_get_books_sort_by_year_asc():
    _create_sample_books(3)
    response = client.get("/books", params={"sort_by": "year", "sort_order": "asc"})
    assert response.status_code == 200
    data = response.json()
    years = [b["year"] for b in data]
    assert years == sorted(years)


def test_get_book_by_id_found():
    books = _create_sample_books(1)
    book_id = books[0]["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id


def test_get_book_by_id_not_found():
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/books/{fake_id}")
    assert response.status_code == 404


def test_delete_book_idempotent():
    books = _create_sample_books(1)
    book_id = books[0]["id"]

    # Перше видалення
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    # Друге видалення того ж id (ідемпотентність)
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204


def test_delete_nonexistent_book_still_204():
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.delete(f"/books/{fake_id}")
    assert response.status_code == 204

