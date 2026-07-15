from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.session import get_db

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        raise AppError("invalid_token", "Invalid or expired token.", 401)

    user = db.get(User, user_id)
    if user is None:
        raise AppError("invalid_token", "Invalid or expired token.", 401)

    return user