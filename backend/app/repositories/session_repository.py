from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UserSession


def create(db: Session, user_id: int, token_hash: str, csrf_token: str, expires_at: datetime) -> UserSession:
    row = UserSession(user_id=user_id, token_hash=token_hash, csrf_token=csrf_token, expires_at=expires_at)
    db.add(row)
    db.flush()
    return row


def get_by_token_hash(db: Session, token_hash: str) -> UserSession | None:
    return db.scalar(select(UserSession).where(UserSession.token_hash == token_hash))


def delete(db: Session, row: UserSession) -> None:
    db.delete(row)
