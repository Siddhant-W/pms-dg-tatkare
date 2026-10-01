from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SupervisorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    full_name: str | None = None
    role: str = "SUPERVISOR"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: SupervisorOut | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
    type: str | None = None
