import uuid
from datetime import datetime, timezone

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.models.refresh_token import RefreshToken


def revoke_all_refresh_tokens(db: Session, user_id: uuid.UUID, reason: str) -> None:
    """Kill every live refresh token for a user. Shared by change-password /
    change-email / reset-password (reason="security_action") and, now, by
    admin account-disable (same reason - a disable should be exactly as
    instant as any other security action, not wait for the access token
    to expire on its own)."""
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc), revoked_reason=reason)
    )