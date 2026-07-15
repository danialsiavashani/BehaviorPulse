from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = decode_access_token(token)
    except JWTError:
        raise AppError("invalid_token", "Invalid or expired token.", 401)

    user = db.get(User, user_id)
    if user is None:
        raise AppError("invalid_token", "Invalid or expired token.", 401)

    return user