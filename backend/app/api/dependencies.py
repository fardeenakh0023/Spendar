from fastapi import Cookie, Depends, Header
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.core.errors import AppError
from app.models import User, UserSession
from app.services import auth_service


def get_current_session(
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
) -> UserSession:
    session = auth_service.get_session(db, session_id)
    if session is None:
        raise AppError(401, "Not authenticated")
    return session


def get_current_user(session: UserSession = Depends(get_current_session)) -> User:
    """For read-only (GET) endpoints."""
    return session.user


def get_csrf_protected_user(
    session: UserSession = Depends(get_current_session),
    x_csrf_token: str | None = Header(default=None),
) -> User:
    """For POST/PATCH/DELETE: also requires the X-CSRF-Token header."""
    if not x_csrf_token or not security.tokens_match(x_csrf_token, session.csrf_token):
        raise AppError(403, "Invalid or missing CSRF token")
    return session.user
