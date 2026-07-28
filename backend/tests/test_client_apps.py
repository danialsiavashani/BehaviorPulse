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


def test_create_app_requires_auth():
    response = client.post("/v1/apps", json={"name": "No Auth App"})
    assert response.status_code == 403


def test_create_app_success():
    token = _signup_and_login()
    response = client.post("/v1/apps", json={"name": "My App"}, headers=_headers(token))

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "My App"
    assert body["client_id"].startswith("client_")


def test_list_apps_only_shows_own_apps():
    token_a = _signup_and_login()
    _create_app(token_a, name="User A App")

    token_b = _signup_and_login()
    _create_app(token_b, name="User B App 1")
    _create_app(token_b, name="User B App 2")

    response = client.get("/v1/apps?page=1&page_size=10", headers=_headers(token_b))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    names = {item["name"] for item in body["items"]}
    assert names == {"User B App 1", "User B App 2"}


def test_get_scopes_empty_for_new_app():
    token = _signup_and_login()
    app_out = _create_app(token)

    response = client.get(f"/v1/apps/{app_out['id']}/scopes", headers=_headers(token))

    assert response.status_code == 200
    assert response.json() == []


def test_set_scope_creates_then_toggles():
    token = _signup_and_login()
    app_out = _create_app(token)

    create_response = client.post(
        f"/v1/apps/{app_out['id']}/scopes",
        json={"service_key": "observations.analyze", "enabled": True},
        headers=_headers(token),
    )
    assert create_response.status_code == 201
    assert create_response.json()["enabled"] is True

    toggle_response = client.post(
        f"/v1/apps/{app_out['id']}/scopes",
        json={"service_key": "observations.analyze", "enabled": False},
        headers=_headers(token),
    )
    assert toggle_response.status_code == 200
    assert toggle_response.json()["enabled"] is False


def test_scopes_not_found_for_someone_elses_app():
    token_a = _signup_and_login()
    app_a = _create_app(token_a)

    token_b = _signup_and_login()
    response = client.get(f"/v1/apps/{app_a['id']}/scopes", headers=_headers(token_b))

    assert response.status_code == 404


def test_delete_app_removes_it():
    token = _signup_and_login()
    app_out = _create_app(token)

    delete_response = client.delete(f"/v1/apps/{app_out['id']}", headers=_headers(token))
    assert delete_response.status_code == 204

    list_response = client.get("/v1/apps?page=1&page_size=10", headers=_headers(token))
    assert list_response.json()["total"] == 0


def test_delete_app_not_found_for_someone_elses_app():
    token_a = _signup_and_login()
    app_a = _create_app(token_a)

    token_b = _signup_and_login()
    response = client.delete(f"/v1/apps/{app_a['id']}", headers=_headers(token_b))

    assert response.status_code == 404