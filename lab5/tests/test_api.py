import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.json == {"status": "ok"}

def test_authors_crud(client):
    # Create author
    rv = client.post("/authors", json={"name": "Test Author"})
    assert rv.status_code == 201
    author_id = rv.json["id"]
    
    # Get authors
    rv = client.get("/authors")
    assert rv.status_code == 200
    assert len(rv.json) >= 1
    
    # Get specific author
    rv = client.get(f"/authors/{author_id}")
    assert rv.status_code == 200
    assert rv.json["name"] == "Test Author"

    # Delete author
    rv = client.delete(f"/authors/{author_id}")
    assert rv.status_code == 200

    # Get specific author (should be 404)
    rv = client.get(f"/authors/{author_id}")
    assert rv.status_code == 404

def test_books_crud(client):
    # Create author first
    rv = client.post("/authors", json={"name": "Test Author"})
    author_id = rv.json["id"]

    # Create book
    rv = client.post("/books", json={
        "title": "Test Book",
        "author_id": author_id,
        "year": 2023,
        "tags": ["fiction"]
    })
    assert rv.status_code == 201
    book_id = rv.json["id"]

    # Get books
    rv = client.get("/books")
    assert rv.status_code == 200
    assert len(rv.json) >= 1

    # Get specific book
    rv = client.get(f"/books/{book_id}")
    assert rv.status_code == 200
    assert rv.json["title"] == "Test Book"

    # Update book
    rv = client.put(f"/books/{book_id}", json={
        "title": "Updated Book",
        "author_id": author_id,
        "year": 2024,
        "tags": ["non-fiction"]
    })
    assert rv.status_code == 200
    assert rv.json["title"] == "Updated Book"

    # Delete book
    rv = client.delete(f"/books/{book_id}")
    assert rv.status_code == 200
