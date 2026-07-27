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


def _create_app(token: str, name: str = "Test App") -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/v1/apps", json={"name": name}, headers=headers)
    assert response.status_code == 201
    return response.json()


def _grant_scope(token: str, client_app_id: str, service_key: str = "observations.analyze") -> None:
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        f"/v1/apps/{client_app_id}/scopes",
        json={"service_key": service_key},
        headers=headers,
    )
    assert response.status_code in (200, 201)


def test_list_services_requires_auth():
    response = client.get("/v1/services")
    assert response.status_code == 403


def test_get_service_success():
    token = _signup_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/v1/services/observations.analyze", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["service_key"] == "observations.analyze"
    assert body["status"] == "active"


def test_get_service_not_found():
    token = _signup_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/v1/services/not_a_real_service", headers=headers)

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_service_apps_not_found_for_bad_service_key():
    token = _signup_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/v1/services/not_a_real_service/apps", headers=headers)

    assert response.status_code == 404


def test_service_apps_empty_before_scope_granted():
    token = _signup_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    _create_app(token)

    response = client.get("/v1/services/observations.analyze/apps", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_service_apps_includes_app_after_scope_granted():
    token = _signup_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    app_out = _create_app(token, name="Scoped App")
    _grant_scope(token, app_out["id"])

    response = client.get("/v1/services/observations.analyze/apps", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == app_out["id"]
    assert body[0]["name"] == "Scoped App"


def test_service_apps_only_shows_current_users_apps():
    token_a = _signup_and_login()
    app_a = _create_app(token_a, name="User A App")
    _grant_scope(token_a, app_a["id"])

    token_b = _signup_and_login()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    response = client.get("/v1/services/observations.analyze/apps", headers=headers_b)

    assert response.status_code == 200
    assert response.json() == []