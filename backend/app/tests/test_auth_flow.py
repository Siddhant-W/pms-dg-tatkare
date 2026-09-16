import pytest

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.supervisor import Supervisor
from app.tests.conftest import TestSessionLocal

USERNAME = "Vaishali"
PASSWORD = "Vaishali"


async def _seed_supervisor() -> Supervisor:
    async with TestSessionLocal() as db:
        supe = Supervisor(
            username=USERNAME,
            hashed_password=get_password_hash(PASSWORD),
            full_name="Mrs. Vaishali Patil",
        )
        db.add(supe)
        await db.commit()
        return supe


def test_password_hashing_roundtrip():
    """Regression: passlib/bcrypt 5.x raised ValueError on every verify()."""
    hashed = get_password_hash(PASSWORD)
    assert hashed.startswith("$2")
    assert verify_password(PASSWORD, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_password_longer_than_bcrypt_limit_does_not_raise():
    """bcrypt only reads 72 bytes; over-long input must not blow up."""
    long_password = "a" * 200
    hashed = get_password_hash(long_password)
    assert verify_password(long_password, hashed) is True


def test_malformed_hash_returns_false_not_error():
    assert verify_password(PASSWORD, "not-a-bcrypt-hash") is False


@pytest.mark.asyncio
async def test_login_success_returns_token_and_refresh_cookie(client):
    await _seed_supervisor()

    resp = await client.post(
        "/api/auth/login", json={"username": USERNAME, "password": PASSWORD}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == USERNAME
    # Password material must never leak back to the client.
    assert "hashed_password" not in body["user"]

    cookie = resp.cookies.get("refresh_token")
    assert cookie, "login must set the refresh cookie"
    assert "httponly" in resp.headers["set-cookie"].lower()


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(client):
    await _seed_supervisor()
    resp = await client.post(
        "/api/auth/login", json={"username": USERNAME, "password": "wrong"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_with_unknown_user_returns_401(client):
    resp = await client.post(
        "/api/auth/login", json={"username": "ghost", "password": "whatever"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_a_token(client):
    resp = await client.get("/api/auth/me")
    # Must be 401 (not 403) so the client interceptor can trigger a refresh.
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_supervisor(client):
    await _seed_supervisor()
    login = await client.post(
        "/api/auth/login", json={"username": USERNAME, "password": PASSWORD}
    )
    token = login.json()["access_token"]

    resp = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == USERNAME


@pytest.mark.asyncio
async def test_refresh_token_is_rejected_as_access_token(client):
    """A refresh token must not authenticate protected routes."""
    supe = await _seed_supervisor()
    refresh = create_refresh_token(supe.id)

    resp = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {refresh}"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_garbage_token_is_rejected(client):
    resp = await client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_token_for_deleted_supervisor_is_rejected(client):
    import uuid

    token = create_access_token(uuid.uuid4())
    resp = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_issues_new_access_token(client):
    await _seed_supervisor()
    login = await client.post(
        "/api/auth/login", json={"username": USERNAME, "password": PASSWORD}
    )
    assert login.status_code == 200

    # client keeps the refresh cookie from the login response
    resp = await client.post("/api/auth/refresh")
    assert resp.status_code == 200

    new_token = resp.json()["access_token"]
    me = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {new_token}"}
    )
    assert me.status_code == 200


@pytest.mark.asyncio
async def test_refresh_without_cookie_returns_401(client):
    resp = await client.post("/api/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_access_token_cannot_be_used_to_refresh(client):
    supe = await _seed_supervisor()
    client.cookies.set("refresh_token", create_access_token(supe.id))

    resp = await client.post("/api/auth/refresh")
    assert resp.status_code == 401
    client.cookies.clear()


@pytest.mark.asyncio
async def test_logout_succeeds_without_a_valid_access_token(client):
    """An expired session must still be able to clear its refresh cookie."""
    resp = await client.post("/api/auth/logout")
    assert resp.status_code == 200
