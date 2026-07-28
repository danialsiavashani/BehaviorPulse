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


def _create_key(token: str, client_app_id: str, name: str = "Test Key") -> dict:
    response = client.post(
        "/v1/api-keys",
        json={"client_app_id": client_app_id, "name": name},
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def test_create_key_success():
    token = _signup_and_login()
    app_out = _create_app(token)

    response = client.post(
        "/v1/api-keys",
        json={"client_app_id": app_out["id"], "name": "Production"},
        headers=_headers(token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Production"
    assert body["raw_key"].startswith("bp_sk_")
    assert body["key_prefix"] == body["raw_key"][:12]


def test_create_key_not_found_for_someone_elses_app():
    token_a = _signup_and_login()
    app_a = _create_app(token_a)

    token_b = _signup_and_login()
    response = client.post(
        "/v1/api-keys",
        json={"client_app_id": app_a["id"], "name": "Sneaky Key"},
        headers=_headers(token_b),
    )

    assert response.status_code == 404


def test_list_keys_requires_client_app_id():
    token = _signup_and_login()
    response = client.get("/v1/api-keys?page=1&page_size=10", headers=_headers(token))
    assert response.status_code == 422


def test_list_keys_scoped_to_app():
    token = _signup_and_login()
    app_out = _create_app(token)
    _create_key(token, app_out["id"], name="Key One")
    _create_key(token, app_out["id"], name="Key Two")

    response = client.get(
        f"/v1/api-keys?client_app_id={app_out['id']}&page=1&page_size=10",
        headers=_headers(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    names = {item["name"] for item in body["items"]}
    assert names == {"Key One", "Key Two"}


def test_revoke_key_success():
    token = _signup_and_login()
    app_out = _create_app(token)
    key = _create_key(token, app_out["id"])

    response = client.post(f"/v1/api-keys/{key['id']}/revoke", headers=_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["revoked_at"] is not None


def test_revoke_key_not_found_for_someone_elses_key():
    token_a = _signup_and_login()
    app_a = _create_app(token_a)
    key_a = _create_key(token_a, app_a["id"])

    token_b = _signup_and_login()
    response = client.post(f"/v1/api-keys/{key_a['id']}/revoke", headers=_headers(token_b))

    assert response.status_code == 404