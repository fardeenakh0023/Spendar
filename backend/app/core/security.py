import hashlib
import secrets
from datetime import datetime, timezone

import bcrypt


def utcnow() -> datetime:
    """Naive UTC datetime (MySQL DATETIME has no timezone)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_session_token() -> tuple[str, str]:
    """Return (raw_token_for_cookie, sha256_hash_for_database)."""
    raw = secrets.token_urlsafe(32)
    return raw, hash_token(raw)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def tokens_match(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
