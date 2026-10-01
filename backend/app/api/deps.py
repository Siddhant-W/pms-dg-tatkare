import uuid as uuid_module

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.security import ALGORITHM, TOKEN_TYPE_ACCESS
from app.core.config import settings
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.schemas.auth import TokenPayload

# auto_error=False so a missing header yields our own 401 (with the correct
# WWW-Authenticate header) instead of FastAPI's default 403.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_supervisor(
    db: AsyncSession = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
) -> Supervisor:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise credentials_exception

    # A refresh token must never be accepted as an access token.
    if token_data.type != TOKEN_TYPE_ACCESS:
        raise credentials_exception

    if not token_data.sub:
        raise credentials_exception

    try:
        supervisor_id = uuid_module.UUID(token_data.sub)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(Supervisor).where(Supervisor.id == supervisor_id))
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception
    return user


async def require_admin(user: Supervisor = Depends(get_current_supervisor)) -> Supervisor:
    """Gate for endpoints that change school-wide setup (teachers, timetable).

    The role is read from the database on every request rather than baked into
    the JWT, so demoting an account takes effect immediately instead of when
    its access token expires.
    """
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
