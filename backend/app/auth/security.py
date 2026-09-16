from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt

from app.core.config import settings

ALGORITHM = "HS256"

# bcrypt only ever considers the first 72 bytes of a secret. Newer bcrypt
# releases raise ValueError instead of silently truncating, so we normalise
# here and keep hashing/verification symmetric.
_BCRYPT_MAX_BYTES = 72

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def _prepare_secret(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def create_access_token(subject: str | Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": TOKEN_TYPE_ACCESS}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": TOKEN_TYPE_REFRESH}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(_prepare_secret(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed / legacy hash in the database: treat as a failed login
        # rather than letting it surface as a 500.
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(_prepare_secret(password), bcrypt.gensalt()).decode("utf-8")
