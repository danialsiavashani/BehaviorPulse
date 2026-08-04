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

def test_unhandled_exception_in_analyze_still_logs_with_client_app_id(monkeypatch):
    """Regression test: require_service_auth resolves the client app before
    the route body runs, but never stashed it on request.state - only
    service_key. The global exception handler (app/core/errors.py) already
    existed and already ran correctly on unhandled exceptions; it just
    always wrote client_app_id=None, since that's all request.state had.
    GET /v1/logs INNER JOINs on client_app_id, so a NULL row can never
    appear there. Not "no log was written" - a log WAS written, just one
    nobody could ever see.

    Uses its own TestClient with raise_server_exceptions=False: Starlette's
    real behavior is to run the registered exception handler, send its
    response to the actual client, and then re-raise the original
    exception afterward purely for server-side visibility (so e.g. Uvicorn
    logs it) - a real HTTP client never sees that re-raise, only the
    response. The module-level `client` defaults to surfacing that re-raise
    (raise_server_exceptions=True), which is the right default for every
    other test in this file - an unhandled exception in a normal test
    should fail loudly, not get silently swallowed into a 500. This test is
    the deliberate exception, since provoking exactly that behavior is the
    point."""
    import app.api.routes.observations as observations_module

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated crash")

    monkeypatch.setattr(observations_module, "run_observation_analytics", _boom)

    lenient_client = TestClient(app, raise_server_exceptions=False)

    token = _signup_and_login()
    app_out = _create_app(token)
    _grant_scope(token, app_out["id"])
    key = _create_api_key(token, app_out["id"])
    service_headers = {"X-Client-Id": app_out["client_id"], "X-Api-Key": key["raw_key"]}

    response = lenient_client.post(
        "/v1/observations/analyze", json=_sample_payload(), headers=service_headers
    )
    assert response.status_code == 500
    assert response.json()["error"] == "internal_error"

    dashboard_headers = {"Authorization": f"Bearer {token}"}
    logs_response = client.get(
        f"/v1/logs?client_app_id={app_out['id']}", headers=dashboard_headers
    )
    body = logs_response.json()
    assert body["total"] == 1
    assert body["items"][0]["status_code"] == 500
    assert body["items"][0]["error_code"] == "internal_error"