import secrets
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


def _full_setup(grant: bool = True) -> tuple[str, str]:
    """Creates a user, app, (optionally) enabled scope, and API key.

    Returns (client_id, raw_api_key).
    """
    token = _signup_and_login()
    app_out = _create_app(token)
    if grant:
        _grant_scope(token, app_out["id"])
    key = _create_api_key(token, app_out["id"])
    return app_out["client_id"], key["raw_key"]


def _sample_payload(num_observations: int = 2) -> dict:
    base_obs = {
        "observed_at": "2026-07-12T12:14:00Z",
        "subject": {"type": "animal", "label": "hummingbird"},
        "source": {"type": "camera", "id": "camera_04"},
        "confidence": 0.88,
        "metadata": {"location": "north_fence"},
    }
    alt_obs = {
        "observed_at": "2026-07-12T13:02:00Z",
        "subject": {"type": "animal", "label": "blue_jay"},
        "source": {"type": "camera", "id": "camera_04"},
        "confidence": 0.81,
        "metadata": {},
    }
    if num_observations == 2:
        observations = [base_obs, alt_obs]
    else:
        observations = [base_obs for _ in range(num_observations)]

    return {
        "observations": observations,
        "options": {
            "timezone": "America/Los_Angeles",
            "date_from": "2026-06-15T00:00:00Z",
            "date_to": "2026-07-15T23:59:59Z",
        },
    }


def test_analyze_success_returns_completed_analysis():
    client_id, raw_key = _full_setup()
    headers = {"X-Client-Id": client_id, "X-Api-Key": raw_key}

    response = client.post("/v1/observations/analyze", json=_sample_payload(), headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["analysis_id"].startswith("ana_")
    assert body["computed_metrics"]["total_observations"] == 2
    assert len(body["computed_metrics"]["top_subjects"]) == 2
    assert 0.0 <= body["computed_confidence"] <= 1.0
    assert isinstance(body["recommendations"], list)
    assert "Predictions are pattern estimates based on historical observations, not guarantees." in body["warnings"]


def test_analyze_missing_api_key_headers():
    response = client.post("/v1/observations/analyze", json=_sample_payload())

    assert response.status_code == 401
    assert response.json()["error"] == "missing_api_key"


def test_analyze_invalid_client_id():
    headers = {"X-Client-Id": "client_doesnotexist", "X-Api-Key": "bp_sk_whatever"}

    response = client.post("/v1/observations/analyze", json=_sample_payload(), headers=headers)

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_api_key"


def test_analyze_wrong_api_key():
    client_id, _real_key = _full_setup()
    wrong_key = f"bp_sk_{secrets.token_hex(24)}"
    headers = {"X-Client-Id": client_id, "X-Api-Key": wrong_key}

    response = client.post("/v1/observations/analyze", json=_sample_payload(), headers=headers)

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_api_key"


def test_analyze_service_not_enabled():
    client_id, raw_key = _full_setup(grant=False)
    headers = {"X-Client-Id": client_id, "X-Api-Key": raw_key}

    response = client.post("/v1/observations/analyze", json=_sample_payload(), headers=headers)

    assert response.status_code == 403
    assert response.json()["error"] == "service_not_enabled"


def test_analyze_payload_too_large():
    client_id, raw_key = _full_setup()
    headers = {"X-Client-Id": client_id, "X-Api-Key": raw_key}
    payload = _sample_payload(num_observations=5001)

    response = client.post("/v1/observations/analyze", json=payload, headers=headers)

    assert response.status_code == 413
    assert response.json()["error"] == "payload_too_large"


def test_analyze_invalid_payload_missing_field():
    client_id, raw_key = _full_setup()
    headers = {"X-Client-Id": client_id, "X-Api-Key": raw_key}
    payload = _sample_payload()
    del payload["observations"][0]["confidence"]

    response = client.post("/v1/observations/analyze", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json()["error"] == "invalid_payload"


def test_analyze_empty_observations_rejected():
    client_id, raw_key = _full_setup()
    headers = {"X-Client-Id": client_id, "X-Api-Key": raw_key}
    payload = _sample_payload()
    payload["observations"] = []

    response = client.post("/v1/observations/analyze", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json()["error"] == "invalid_payload"