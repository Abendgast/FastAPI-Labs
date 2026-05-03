import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from lab7.main import app
from lab7.auth import get_current_user

client = TestClient(app)

@pytest.fixture
def mock_redis():
    with patch("lab7.rate_limit.redis_client") as mock:
        mock.zremrangebyscore = AsyncMock()
        mock.zcard = AsyncMock()
        mock.zadd = AsyncMock()
        mock.expire = AsyncMock()
        yield mock

def test_anonymous_under_limit(mock_redis):
    mock_redis.zcard.return_value = 1
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ok", "docs": "/docs"}

def test_anonymous_over_limit(mock_redis):
    mock_redis.zcard.return_value = 2
    response = client.get("/")
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}

def test_authenticated_under_limit(mock_redis):
    app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}
    mock_redis.zcard.return_value = 9
    response = client.get("/books")
    assert response.status_code == 200
    app.dependency_overrides.clear()

def test_authenticated_over_limit(mock_redis):
    app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}
    mock_redis.zcard.return_value = 10
    response = client.get("/books")
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}
    app.dependency_overrides.clear()
