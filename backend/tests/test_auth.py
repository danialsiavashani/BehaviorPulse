import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _random_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_signup_creates_user():
    email = _random_email()
    response = client.post("/v1/auth/signup", json={"email": email, "password": "testpass123"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert "password_hash" not in body


def test_signup_duplicate_email_fails():
    email = _random_email()
    client.post("/v1/auth/signup", json={"email": email, "password": "testpass123"})
    response = client.post("/v1/auth/signup", json={"email": email, "password": "testpass123"})
    assert response.status_code == 409
    assert response.json()["error"] == "email_taken"


def test_login_success_returns_token():
    email = _random_email()
    client.post("/v1/auth/signup", json={"email": email, "password": "testpass123"})
    response = client.post("/v1/auth/login", json={"email": email, "password": "testpass123"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_fails():
    email = _random_email()
    client.post("/v1/auth/signup", json={"email": email, "password": "testpass123"})
    response = client.post("/v1/auth/login", json={"email": email, "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_credentials"


def test_me_with_valid_token_returns_user():
    email = _random_email()
    client.post("/v1/auth/signup", json={"email": email, "password": "testpass123"})
    login_response = client.post("/v1/auth/login", json={"email": email, "password": "testpass123"})
    token = login_response.json()["access_token"]

    response = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_me_without_token_fails():
    response = client.get("/v1/auth/me")
    assert response.status_code == 401