import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def _random_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def _signup(email: str, password: str = "testpass123") -> None:
    response = client.post("/v1/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 201


def _login(email: str, password: str = "testpass123") -> dict:
    response = client.post("/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def _signup_and_login() -> tuple[str, dict]:
    email = _random_email()
    _signup(email)
    return email, _login(email)

class _FakeEmailClient:
    """Stands in for whatever real EmailClient get_email_client() would
    otherwise return (SMTPEmailClient or ConsoleEmailClient, depending on
    ambient settings.smtp_* config). Tests that need the raw reset link
    should patch get_email_client() to return this, rather than patching a
    specific concrete class - that way the test passes identically whether
    it runs locally with real SMTP configured, or in CI with none at all."""

    def __init__(self) -> None:
        self.captured: dict = {}

    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        self.captured["reset_link"] = reset_link


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


# --- refresh, rotation, reuse detection ---------------------------------


def test_refresh_returns_new_pair():
    _, tokens = _signup_and_login()

    response = client.post("/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    new_tokens = response.json()
    # Access tokens are deterministic JWTs - same claims + same second can
    # legitimately produce a byte-identical token, so that's not what we
    # check here. The refresh token is what must always be different.
    assert new_tokens["refresh_token"] != tokens["refresh_token"]


def test_refresh_rotates_old_token_dead():
    _, tokens = _signup_and_login()
    client.post("/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    response = client.post("/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200


def test_refresh_reuse_after_grace_period_revokes_all_sessions(monkeypatch):
    monkeypatch.setattr(settings, "refresh_reuse_grace_seconds", 0)

    _, tokens = _signup_and_login()
    refresh_response = client.post(
        "/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    new_tokens = refresh_response.json()

    reuse_response = client.post(
        "/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert reuse_response.status_code == 401

    blast_radius_response = client.post(
        "/v1/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert blast_radius_response.status_code == 401


def test_refresh_invalid_token_rejected():
    response = client.post("/v1/auth/refresh", json={"refresh_token": "not_a_real_token"})
    assert response.status_code == 401


# --- logout ---------------------------------------------------------------


def test_logout_revokes_token_immediately_no_grace_period():
    _, tokens = _signup_and_login()

    logout_response = client.post(
        "/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
    )
    assert logout_response.status_code == 204

    # Unlike rotation, a logged-out token gets no benefit of the doubt,
    # even immediately afterward - this is a deliberate kill, not a race.
    refresh_response = client.post(
        "/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 401


def test_logout_idempotent_on_unknown_token():
    response = client.post("/v1/auth/logout", json={"refresh_token": "not_a_real_token"})
    assert response.status_code == 204


# --- forgot / reset password ----------------------------------------------


def test_forgot_password_always_returns_204():
    known_response = client.post(
        "/v1/auth/forgot-password", json={"email": _random_email()}
    )
    assert known_response.status_code == 204

    email, _ = _signup_and_login()
    existing_response = client.post("/v1/auth/forgot-password", json={"email": email})
    assert existing_response.status_code == 204


def test_reset_password_flow(monkeypatch):
    fake_client = _FakeEmailClient()
    monkeypatch.setattr("app.api.routes.auth.get_email_client", lambda: fake_client)

    email = _random_email()
    _signup(email)

    client.post("/v1/auth/forgot-password", json={"email": email})
    token = fake_client.captured["reset_link"].split("token=")[1]

    reset_response = client.post(
        "/v1/auth/reset-password", json={"token": token, "new_password": "newpass456"}
    )
    assert reset_response.status_code == 200

    old_password_login = client.post(
        "/v1/auth/login", json={"email": email, "password": "testpass123"}
    )
    assert old_password_login.status_code == 401

    new_password_login = client.post(
        "/v1/auth/login", json={"email": email, "password": "newpass456"}
    )
    assert new_password_login.status_code == 200


def test_reset_password_token_cannot_be_reused(monkeypatch):
    fake_client = _FakeEmailClient()
    monkeypatch.setattr("app.api.routes.auth.get_email_client", lambda: fake_client)

    email = _random_email()
    _signup(email)
    client.post("/v1/auth/forgot-password", json={"email": email})
    token = fake_client.captured["reset_link"].split("token=")[1]

    first_response = client.post(
        "/v1/auth/reset-password", json={"token": token, "new_password": "newpass456"}
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/v1/auth/reset-password", json={"token": token, "new_password": "anotherpass789"}
    )
    assert second_response.status_code == 400

def test_reset_password_invalid_token_rejected():
    response = client.post(
        "/v1/auth/reset-password", json={"token": "not_a_real_token", "new_password": "newpass456"}
    )
    assert response.status_code == 400


# --- change password --------------------------------------------------------


def test_change_password_wrong_current_password_rejected():
    _, tokens = _signup_and_login()

    response = client.post(
        "/v1/auth/change-password",
        json={"current_password": "wrongpassword", "new_password": "newpass456"},
        headers=_headers(tokens["access_token"]),
    )
    assert response.status_code == 401


def test_change_password_revokes_other_sessions():
    email, session_a = _signup_and_login()
    session_b = _login(email)

    response = client.post(
        "/v1/auth/change-password",
        json={"current_password": "testpass123", "new_password": "newpass456"},
        headers=_headers(session_a["access_token"]),
    )
    assert response.status_code == 200
    new_tokens = response.json()

    survives_response = client.post(
        "/v1/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]}
    )
    assert survives_response.status_code == 200

    dead_response = client.post(
        "/v1/auth/refresh", json={"refresh_token": session_b["refresh_token"]}
    )
    assert dead_response.status_code == 401


# --- change email --------------------------------------------------------


def test_change_email_wrong_password_rejected():
    _, tokens = _signup_and_login()

    response = client.post(
        "/v1/auth/change-email",
        json={"current_password": "wrongpassword", "new_email": _random_email()},
        headers=_headers(tokens["access_token"]),
    )
    assert response.status_code == 401


def test_change_email_duplicate_rejected():
    other_email = _random_email()
    _signup(other_email)

    _, tokens = _signup_and_login()

    response = client.post(
        "/v1/auth/change-email",
        json={"current_password": "testpass123", "new_email": other_email},
        headers=_headers(tokens["access_token"]),
    )
    assert response.status_code == 409


def test_change_email_success():
    _, tokens = _signup_and_login()
    new_email = _random_email()

    response = client.post(
        "/v1/auth/change-email",
        json={"current_password": "testpass123", "new_email": new_email},
        headers=_headers(tokens["access_token"]),
    )
    assert response.status_code == 200

    login_response = client.post(
        "/v1/auth/login", json={"email": new_email, "password": "testpass123"}
    )
    assert login_response.status_code == 200


# --- delete account --------------------------------------------------------


def test_delete_account_removes_user():
    email, tokens = _signup_and_login()

    response = client.delete("/v1/auth/me", headers=_headers(tokens["access_token"]))
    assert response.status_code == 204

    login_response = client.post(
        "/v1/auth/login", json={"email": email, "password": "testpass123"}
    )
    assert login_response.status_code == 401

    resignup_response = client.post(
        "/v1/auth/signup", json={"email": email, "password": "testpass123"}
    )
    assert resignup_response.status_code == 201


def test_delete_account_requires_auth():
    response = client.delete("/v1/auth/me")
    assert response.status_code == 403