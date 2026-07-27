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


def _create_api_key(token: str, client_app_id: str, name: str = "Test Key") -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/v1/api-keys",
        json={"client_app_id": client_app_id, "name": name},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def _sample_payload() -> dict:
    return {
        "observations": [
            {
                "observed_at": "2026-07-12T12:14:00Z",
                "subject": {"type": "animal", "label": "hummingbird"},
                "source": {"type": "camera", "id": "camera_04"},
                "confidence": 0.88,
                "metadata": {},
            }
        ],
        "options": {
            "timezone": "America/Los_Angeles",
            "date_from": "2026-06-15T00:00:00Z",
            "date_to": "2026-07-15T23:59:59Z",
        },
    }


def test_usage_requires_auth():
    response = client.get("/v1/usage")
    assert response.status_code == 403


def test_usage_zero_for_new_user_with_no_requests():
    token = _signup_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/v1/usage", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total_requests"] == 0
    assert body["success_rate"] == 0.0
    assert body["by_app"] == []


def test_usage_service_key_filter_matches_unfiltered_with_single_service():
    token = _signup_and_login()
    dashboard_headers = {"Authorization": f"Bearer {token}"}
    app_out = _create_app(token)
    _grant_scope(token, app_out["id"])
    key = _create_api_key(token, app_out["id"])

    service_headers = {"X-Client-Id": app_out["client_id"], "X-Api-Key": key["raw_key"]}
    analyze_response = client.post(
        "/v1/observations/analyze", json=_sample_payload(), headers=service_headers
    )
    assert analyze_response.status_code == 200

    unfiltered = client.get("/v1/usage", headers=dashboard_headers).json()
    filtered = client.get(
        "/v1/usage?service_key=observations.analyze", headers=dashboard_headers
    ).json()

    assert unfiltered["total_requests"] == 1
    assert filtered["total_requests"] == unfiltered["total_requests"]
    assert filtered["by_app"] == unfiltered["by_app"]


def test_usage_service_key_filter_unknown_key_returns_zero():
    token = _signup_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    app_out = _create_app(token)
    _grant_scope(token, app_out["id"])
    key = _create_api_key(token, app_out["id"])
    service_headers = {"X-Client-Id": app_out["client_id"], "X-Api-Key": key["raw_key"]}
    client.post("/v1/observations/analyze", json=_sample_payload(), headers=service_headers)

    response = client.get("/v1/usage?service_key=does_not_exist", headers=headers)

    assert response.status_code == 200
    assert response.json()["total_requests"] == 0