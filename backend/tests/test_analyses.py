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


def _grant_scope(token: str, client_app_id: str, service_key: str = "observations.analyze") -> None:
    response = client.post(
        f"/v1/apps/{client_app_id}/scopes",
        json={"service_key": service_key},
        headers=_headers(token),
    )
    assert response.status_code in (200, 201)


def _create_api_key(token: str, client_app_id: str, name: str = "Test Key") -> dict:
    response = client.post(
        "/v1/api-keys",
        json={"client_app_id": client_app_id, "name": name},
        headers=_headers(token),
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


def _run_real_analysis(token: str, app_out: dict) -> dict:
    _grant_scope(token, app_out["id"])
    key = _create_api_key(token, app_out["id"])
    service_headers = {"X-Client-Id": app_out["client_id"], "X-Api-Key": key["raw_key"]}
    response = client.post(
        "/v1/observations/analyze", json=_sample_payload(), headers=service_headers
    )
    assert response.status_code == 200
    return response.json()


def test_list_analyses_requires_auth():
    response = client.get("/v1/analyses")
    assert response.status_code == 403


def test_list_analyses_empty_for_new_user():
    token = _signup_and_login()
    response = client.get("/v1/analyses?page=1&page_size=10", headers=_headers(token))

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_list_analyses_shows_completed_run():
    token = _signup_and_login()
    app_out = _create_app(token)
    _run_real_analysis(token, app_out)

    response = client.get("/v1/analyses?page=1&page_size=10", headers=_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["app_name"] == app_out["name"]


def test_list_analyses_only_shows_own_apps_analyses():
    token_a = _signup_and_login()
    app_a = _create_app(token_a)
    _run_real_analysis(token_a, app_a)

    token_b = _signup_and_login()
    response = client.get("/v1/analyses?page=1&page_size=10", headers=_headers(token_b))

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_analysis_detail_success():
    token = _signup_and_login()
    app_out = _create_app(token)
    analysis = _run_real_analysis(token, app_out)

    response = client.get(f"/v1/analyses/{analysis['analysis_id']}", headers=_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["analysis_id"] == analysis["analysis_id"]
    assert body["prediction"]
    assert isinstance(body["pattern_table"], list)


def test_get_analysis_detail_not_found():
    token = _signup_and_login()
    response = client.get("/v1/analyses/ana_doesnotexist", headers=_headers(token))
    assert response.status_code == 404


def test_get_analysis_detail_not_found_for_someone_elses_analysis():
    token_a = _signup_and_login()
    app_a = _create_app(token_a)
    analysis = _run_real_analysis(token_a, app_a)

    token_b = _signup_and_login()
    response = client.get(f"/v1/analyses/{analysis['analysis_id']}", headers=_headers(token_b))

    assert response.status_code == 404