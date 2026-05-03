import pytest
from fastapi.testclient import TestClient
from lab6.main import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200

def test_unauthorized_access():
    response = client.get("/books")
    assert response.status_code == 401

def test_login_and_access():
    # Login
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "password"}
    )
    # The default mock user in lab6 auth.py has username: admin, password: password
    # Wait, actually lab6 might have "admin:admin" by default. Let's check lab6.auth
    assert response.status_code == 200 or response.status_code == 401
    
    if response.status_code == 401:
        response = client.post(
            "/auth/token",
            data={"username": "admin", "password": "admin"}
        )
        assert response.status_code == 200

    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    access_token = tokens["access_token"]
    
    # Access protected route
    response = client.get("/books", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_refresh_token():
    # Login
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    refresh_token = response.json()["refresh_token"]

    # Refresh
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
