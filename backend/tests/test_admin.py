import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models.admin_action_log import AdminActionLog
from app.db.models.user import User
from app.db.session import SessionLocal
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


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


def _promote_to_admin(email: str) -> None:
    """No HTTP path makes an admin from nothing, by design - promote_admin.py
    and this helper are the only two ways, same as production."""
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        user.role = "admin"
        db.commit()
    finally:
        db.close()


def _admin_signup_and_login() -> tuple[str, dict]:
    email, tokens = _signup_and_login()
    _promote_to_admin(email)
    # Role isn't baked into the access token's claims (only sub + tv), so
    # the token issued before promotion is already admin-valid - no
    # re-login needed.
    return email, tokens


def _get_user_id(admin_token: str, email: str) -> str:
    response = client.get(f"/v1/admin/users?search={email}", headers=_headers(admin_token))
    return response.json()["items"][0]["id"]


# --- access control ---------------------------------------------------------


def test_admin_endpoints_reject_unauthenticated():
    response = client.get("/v1/admin/users")
    assert response.status_code == 403


def test_admin_endpoints_reject_non_admin():
    _, tokens = _signup_and_login()

    response = client.get("/v1/admin/users", headers=_headers(tokens["access_token"]))
    assert response.status_code == 403


def test_admin_me_returns_admin_role():
    _, tokens = _admin_signup_and_login()

    response = client.get("/v1/admin/me", headers=_headers(tokens["access_token"]))
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


# --- list / get -------------------------------------------------------------


def test_list_users_shape_and_pagination():
    _, admin_tokens = _admin_signup_and_login()
    _signup_and_login()
    _signup_and_login()

    response = client.get(
        "/v1/admin/users?page=1&page_size=10", headers=_headers(admin_tokens["access_token"])
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 3
    item = body["items"][0]
    for field in ("id", "email", "role", "is_active", "is_demo", "app_count", "request_count"):
        assert field in item


def test_list_users_search_by_email():
    _, admin_tokens = _admin_signup_and_login()
    target_email, _ = _signup_and_login()

    response = client.get(
        f"/v1/admin/users?search={target_email}", headers=_headers(admin_tokens["access_token"])
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["email"] == target_email


def test_list_users_filter_by_is_active():
    _, admin_tokens = _admin_signup_and_login()
    target_email, _ = _signup_and_login()
    target_id = _get_user_id(admin_tokens["access_token"], target_email)

    client.patch(
        f"/v1/admin/users/{target_id}",
        json={"is_active": False},
        headers=_headers(admin_tokens["access_token"]),
    )

    # Scoped by search too - is_active alone would also match every
    # disabled user any other test in this run has created.
    disabled_response = client.get(
        f"/v1/admin/users?search={target_email}&is_active=false",
        headers=_headers(admin_tokens["access_token"]),
    )
    assert disabled_response.json()["total"] == 1

    active_response = client.get(
        f"/v1/admin/users?search={target_email}&is_active=true",
        headers=_headers(admin_tokens["access_token"]),
    )
    assert active_response.json()["total"] == 0


def test_get_user_returns_metadata_not_app_details():
    _, admin_tokens = _admin_signup_and_login()
    target_email, target_tokens = _signup_and_login()
    client.post("/v1/apps", json={"name": "Some App"}, headers=_headers(target_tokens["access_token"]))
    target_id = _get_user_id(admin_tokens["access_token"], target_email)

    response = client.get(
        f"/v1/admin/users/{target_id}", headers=_headers(admin_tokens["access_token"])
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == target_email
    assert body["app_count"] == 1
    assert "apps" not in body
    assert "api_keys" not in body


def test_get_user_not_found():
    _, admin_tokens = _admin_signup_and_login()
    response = client.get(
        f"/v1/admin/users/{uuid.uuid4()}", headers=_headers(admin_tokens["access_token"])
    )
    assert response.status_code == 404


# --- update: role change + audit log ----------------------------------------


def test_update_user_change_role_writes_audit_log():
    _, admin_tokens = _admin_signup_and_login()
    target_email, _ = _signup_and_login()
    target_id = _get_user_id(admin_tokens["access_token"], target_email)

    response = client.patch(
        f"/v1/admin/users/{target_id}",
        json={"role": "admin"},
        headers=_headers(admin_tokens["access_token"]),
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

    db = SessionLocal()
    try:
        log = db.scalar(
            select(AdminActionLog).where(
                AdminActionLog.target_user_id == uuid.UUID(target_id),
                AdminActionLog.action == "change_role",
            )
        )
        assert log is not None
        assert log.previous_value == "user"
        assert log.new_value == "admin"
    finally:
        db.close()


# --- update: disable, instant revoke, is_active enforcement -----------------


def test_disable_user_blocks_next_authenticated_request():
    _, admin_tokens = _admin_signup_and_login()
    target_email, target_tokens = _signup_and_login()
    target_id = _get_user_id(admin_tokens["access_token"], target_email)

    disable_response = client.patch(
        f"/v1/admin/users/{target_id}",
        json={"is_active": False},
        headers=_headers(admin_tokens["access_token"]),
    )
    assert disable_response.status_code == 200
    assert disable_response.json()["is_active"] is False

    # Same access token as before disable - still cryptographically valid
    # and unexpired, but is_active is checked fresh against the DB row on
    # every request.
    me_response = client.get("/v1/auth/me", headers=_headers(target_tokens["access_token"]))
    assert me_response.status_code == 403
    assert me_response.json()["error"] == "account_disabled"


def test_disable_user_revokes_refresh_tokens_immediately():
    _, admin_tokens = _admin_signup_and_login()
    target_email, target_tokens = _signup_and_login()
    target_id = _get_user_id(admin_tokens["access_token"], target_email)

    client.patch(
        f"/v1/admin/users/{target_id}",
        json={"is_active": False},
        headers=_headers(admin_tokens["access_token"]),
    )

    refresh_response = client.post(
        "/v1/auth/refresh", json={"refresh_token": target_tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 401


# --- guards -------------------------------------------------------------------


def test_cannot_modify_own_account_via_admin_panel():
    admin_email, admin_tokens = _admin_signup_and_login()
    admin_id = _get_user_id(admin_tokens["access_token"], admin_email)

    response = client.patch(
        f"/v1/admin/users/{admin_id}",
        json={"is_active": False},
        headers=_headers(admin_tokens["access_token"]),
    )
    assert response.status_code == 403
    assert response.json()["error"] == "cannot_modify_self"


def test_count_other_active_admins_excludes_target():
    """Direct check of the last-admin guard's counting logic, not an HTTP
    test. The self-lockout check in update_user already guarantees
    current_admin.id != target.id, and reaching this endpoint at all
    requires current_admin to be an active admin - so
    _count_other_active_admins always finds at least that one admin, and
    the 409 branch in update_user can't be triggered through this router
    alone today. Kept as a defensive check for any future admin-modifying
    path that isn't self-scoped the same way (e.g. a bulk action). This
    test verifies the helper's counting logic directly instead of
    pretending to exercise the currently-unreachable HTTP branch."""
    from app.api.routes.admin import _count_other_active_admins

    admin_a_email, _ = _admin_signup_and_login()
    admin_b_email, _ = _signup_and_login()
    _promote_to_admin(admin_b_email)

    db = SessionLocal()
    try:
        admin_a = db.scalar(select(User).where(User.email == admin_a_email))
        admin_b = db.scalar(select(User).where(User.email == admin_b_email))

        assert _count_other_active_admins(db, excluding_user_id=admin_b.id) >= 1
        assert _count_other_active_admins(db, excluding_user_id=admin_a.id) >= 1
    finally:
        db.close()


def test_disabled_admin_loses_admin_access():
    """A disabled admin isn't just a disabled regular user - get_current_admin_user
    depends on get_current_user, so the is_active check applies to admin
    routes too, not only /dashboard-facing ones."""
    _, admin_a_tokens = _admin_signup_and_login()
    admin_b_email, admin_b_tokens = _admin_signup_and_login()
    admin_b_id = _get_user_id(admin_a_tokens["access_token"], admin_b_email)

    disable_response = client.patch(
        f"/v1/admin/users/{admin_b_id}",
        json={"is_active": False},
        headers=_headers(admin_a_tokens["access_token"]),
    )
    assert disable_response.status_code == 200

    # admin_b's still-unexpired, still-cryptographically-valid access token
    # should now be rejected on admin routes too, not just regular ones.
    me_response = client.get("/v1/admin/me", headers=_headers(admin_b_tokens["access_token"]))
    assert me_response.status_code == 403


def test_demoted_admin_loses_admin_access_immediately():
    """Role isn't baked into the JWT (only sub + tv), so a demotion takes
    effect on the very next request with the same, still-valid access
    token - no re-login or token refresh needed for it to take hold."""
    _, admin_a_tokens = _admin_signup_and_login()
    admin_b_email, admin_b_tokens = _admin_signup_and_login()
    admin_b_id = _get_user_id(admin_a_tokens["access_token"], admin_b_email)

    demote_response = client.patch(
        f"/v1/admin/users/{admin_b_id}",
        json={"role": "user"},
        headers=_headers(admin_a_tokens["access_token"]),
    )
    assert demote_response.status_code == 200

    me_response = client.get("/v1/admin/me", headers=_headers(admin_b_tokens["access_token"]))
    assert me_response.status_code == 403