from typing import Generator
from uuid import UUID
import sys
from pathlib import Path
import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Прапорець, щоб API не підключався до Postgres під час тестів
os.environ["TESTING"] = "1"

# Додаємо корінь проекту в sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lab2.db import Base, get_session  # noqa: E402
from lab2.main import app  # noqa: E402


SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    # Необхідно для anyio/pytest інтеграції (async тестів усередині FastAPI)
    return "asyncio"


def _create_engine_sync():
    async def _create():
        engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return engine

    return asyncio.run(_create())


@pytest.fixture(scope="session")
def test_engine():
    engine = _create_engine_sync()
    yield engine
    asyncio.run(engine.dispose())


def _create_session_sync(test_engine) -> AsyncSession:
    async def _create():
        async_session = async_sessionmaker(
            bind=test_engine, expire_on_commit=False, class_=AsyncSession
        )
        async with async_session() as session:
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())
            await session.commit()
            return session

    return asyncio.run(_create())


@pytest.fixture(scope="function")
def test_session(test_engine) -> AsyncSession:
    return _create_session_sync(test_engine)


@pytest.fixture(scope="function")
def client(test_session: AsyncSession) -> Generator[TestClient, None, None]:
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _create_sample_books(client: TestClient, count: int = 3) -> list[dict]:
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


def test_create_book_success(client: TestClient):
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
    UUID(data["id"])


def test_create_book_validation_error(client: TestClient):
    response = client.post(
        "/books",
        json={
            "author": "Test Author",
            "year": -1,
        },
    )
    assert response.status_code == 422


def test_get_all_books_basic_with_pagination(client: TestClient):
    _create_sample_books(client, 5)
    response = client.get("/books", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_get_books_second_page(client: TestClient):
    _create_sample_books(client, 5)
    response = client.get("/books", params={"limit": 2, "offset": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 2
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_get_books_filter_by_status(client: TestClient):
    _create_sample_books(client, 4)
    response = client.get("/books", params={"status": "available"})
    assert response.status_code == 200
    data = response.json()
    assert all(book["status"] == "available" for book in data["items"])


def test_get_books_filter_by_author_partial(client: TestClient):
    _create_sample_books(client, 3)
    response = client.get("/books", params={"author": "author 1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert all(
        "author 1".lower() in book["author"].lower() for book in data["items"]
    )


def test_get_books_sort_by_title_desc(client: TestClient):
    _create_sample_books(client, 3)
    response = client.get("/books", params={"sort_by": "title", "sort_order": "desc"})
    assert response.status_code == 200
    data = response.json()
    titles = [b["title"] for b in data["items"]]
    assert titles == sorted(titles, key=lambda x: x.lower(), reverse=True)


def test_get_books_sort_by_year_asc(client: TestClient):
    _create_sample_books(client, 3)
    response = client.get("/books", params={"sort_by": "year", "sort_order": "asc"})
    assert response.status_code == 200
    data = response.json()
    years = [b["year"] for b in data["items"]]
    assert years == sorted(years)


def test_get_book_by_id_found(client: TestClient):
    books = _create_sample_books(client, 1)
    book_id = books[0]["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id


def test_get_book_by_id_not_found(client: TestClient):
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/books/{fake_id}")
    assert response.status_code == 404


def test_delete_book_idempotent(client: TestClient):
    books = _create_sample_books(client, 1)
    book_id = books[0]["id"]

    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204


def test_delete_nonexistent_book_still_204(client: TestClient):
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.delete(f"/books/{fake_id}")
    assert response.status_code == 204

