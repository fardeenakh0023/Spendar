from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.errors import AppError
from app.models import User, UserSession
from app.repositories import session_repository, user_repository
from app.schemas.user import LoginRequest, RegisterRequest
from app.services import category_service

# Used to keep login timing similar when the user does not exist.
_DUMMY_HASH = security.hash_password("not-a-real-password")


def register(db: Session, data: RegisterRequest) -> User:
    if user_repository.get_by_username(db, data.username):
        raise AppError(409, "Username is already taken")
    if user_repository.get_by_email(db, data.email):
        raise AppError(409, "Email is already registered")
    try:
        user = user_repository.create(db, data.username, data.email, security.hash_password(data.password))
        category_service.seed_defaults(db, user.id)
        db.commit()
    except IntegrityError:  # two requests raced past the checks above
        db.rollback()
        raise AppError(409, "Username or email is already in use")
    return user


def login(db: Session, data: LoginRequest) -> tuple[str, UserSession]:
    user = user_repository.get_by_identifier(db, data.identifier.strip())
    hashed = user.hashed_password if user else _DUMMY_HASH
    valid = security.verify_password(data.password, hashed)
    if not user or not valid:
        raise AppError(401, "Invalid username/email or password")
    raw, token_hash = security.generate_session_token()
    expires = security.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
    session = session_repository.create(db, user.id, token_hash, security.generate_csrf_token(), expires)
    db.commit()
    return raw, session


def get_session(db: Session, raw_token: str | None) -> UserSession | None:
    """Return the live session for a cookie value, deleting it if expired."""
    if not raw_token:
        return None
    session = session_repository.get_by_token_hash(db, security.hash_token(raw_token))
    if session is None:
        return None
    if session.expires_at <= security.utcnow():
        session_repository.delete(db, session)
        db.commit()
        return None
    return session


def logout(db: Session, session: UserSession) -> None:
    session_repository.delete(db, session)
    db.commit()
