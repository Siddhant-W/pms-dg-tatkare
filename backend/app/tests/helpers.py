"""Shared test helpers (kept out of conftest so they can be imported by name)."""
from functools import lru_cache

from app.auth.security import create_access_token, get_password_hash
from app.models.supervisor import Supervisor
from app.tests.conftest import TestSessionLocal


@lru_cache(maxsize=None)
def _hash(password: str) -> str:
    # bcrypt is deliberately slow; hashing the same test password once keeps the suite fast.
    return get_password_hash(password)


async def make_supervisor(username: str = "admin", role: str = "ADMIN", password: str = "pw-12345") -> dict:
    """Insert a supervisor and return ``{"id", "headers"}`` ready for API calls."""
    async with TestSessionLocal() as db:
        user = Supervisor(
            username=username,
            hashed_password=_hash(password),
            full_name=username.title(),
            role=role,
        )
        db.add(user)
        await db.commit()
        return {"id": user.id, "headers": {"Authorization": f"Bearer {create_access_token(user.id)}"}}
