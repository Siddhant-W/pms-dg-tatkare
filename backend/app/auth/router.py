import uuid as uuid_module

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_supervisor
from app.auth.security import (
    ALGORITHM,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.schemas.auth import LoginRequest, SupervisorOut, Token

router = APIRouter()

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/auth"


def _set_refresh_cookie(response: Response, token: str) -> None:
    is_production = settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        # "lax" keeps the cookie working for the dev setup (Vite on :5173
        # proxying to the API on :8000). "strict" broke silent refresh.
        samesite="none" if is_production else "lax",
        secure=is_production,
        path=REFRESH_COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


def _clear_refresh_cookie(response: Response) -> None:
    is_production = settings.ENVIRONMENT.lower() == "production"
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        samesite="none" if is_production else "lax",
        secure=is_production,
    )


@router.post("/login", response_model=Token)
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supervisor).where(Supervisor.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(user.id)
    refresh_token_value = create_refresh_token(user.id)
    _set_refresh_cookie(response, refresh_token_value)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = uuid_module.UUID(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(Supervisor).where(Supervisor.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Rotate the refresh cookie so a long-lived session keeps a fresh expiry.
    _set_refresh_cookie(response, create_refresh_token(user.id))

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=SupervisorOut)
async def read_me(current_user: Supervisor = Depends(get_current_supervisor)):
    return current_user


@router.post("/logout")
async def logout(response: Response):
    # Logout must succeed even when the access token has already expired,
    # otherwise the client can never clear its refresh cookie.
    _clear_refresh_cookie(response)
    return {"message": "Logged out successfully"}
