import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _random_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def _signup_and_login() -> str:
    email = _random_email()
    client.post("/v1/auth/signup", json={"email": email, "password": "testpass123"})
    login_response = client.post("/v1/auth/login", json={"email": email, "password": "testpass123"})
    return login_response.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_app(token: str, name: str = "Test App") -> dict:
    response = client.post("/v1/apps", json={"name": name}, headers=_headers(token))
    assert response.status_code == 201
    return response.json()


def _create_api_key(token: str, client_app_id: str, name: str = "Test Key") -> dict:
    response = client.post(
        "/v1/api-keys",
        json={"client_app_id": client_app_id, "name": name},
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def _generate_failed_log_row(token: str, app_out: dict) -> None:
    """Triggers a cheap, real service_not_enabled failure - this still
    writes a real ApiRequestLog row tied to a valid client_app_id, without
    needing a full LLM call."""
    key = _create_api_key(token, app_out["id"])
    service_headers = {"X-Client-Id": app_out["client_id"], "X-Api-Key": key["raw_key"]}
    response = client.post(
        "/v1/observations/analyze",
        json={"observations": [], "options": {}},
        headers=service_headers,
    )
    assert response.status_code in (403, 422)


def test_list_logs_requires_auth():
    response = client.get("/v1/logs")
    assert response.status_code == 403


def test_list_logs_empty_for_new_user():
    token = _signup_and_login()
    response = client.get("/v1/logs?page=1&page_size=10", headers=_headers(token))

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_list_logs_shows_failed_request():
    token = _signup_and_login()
    app_out = _create_app(token)
    _generate_failed_log_row(token, app_out)

    response = client.get("/v1/logs?page=1&page_size=10", headers=_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(item["client_app_id"] == app_out["id"] for item in body["items"])


def test_list_logs_filters_by_client_app_id():
    token = _signup_and_login()
    app_a = _create_app(token, name="App A")
    app_b = _create_app(token, name="App B")
    _generate_failed_log_row(token, app_a)
    _generate_failed_log_row(token, app_b)

    response = client.get(
        f"/v1/logs?client_app_id={app_a['id']}&page=1&page_size=10", headers=_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert all(item["client_app_id"] == app_a["id"] for item in body["items"])


def test_list_logs_only_shows_own_apps_logs():
    token_a = _signup_and_login()
    app_a = _create_app(token_a)
    _generate_failed_log_row(token_a, app_a)

    token_b = _signup_and_login()
    response = client.get("/v1/logs?page=1&page_size=10", headers=_headers(token_b))

    assert response.status_code == 200
    assert response.json()["total"] == 0