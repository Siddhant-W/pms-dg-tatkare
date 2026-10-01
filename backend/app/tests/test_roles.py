import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select

from app.api.deps import require_admin
from app.core.migrations import ensure_schema
from app.models.supervisor import Supervisor
from app.seeds.manage_supervisor import upsert_supervisor
from app.tests.conftest import TestSessionLocal
from app.tests.helpers import make_supervisor


@pytest.fixture
async def legacy_engine(tmp_path):
    """A database created by the pre-roles version of the app."""
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'legacy.db'}")
    async with engine.begin() as conn:
        await conn.execute(text(
            "CREATE TABLE supervisors (id CHAR(32) PRIMARY KEY, username VARCHAR, "
            "hashed_password VARCHAR, full_name VARCHAR, created_at DATETIME)"
        ))
        await conn.execute(text("INSERT INTO supervisors (id, username) VALUES ('a', 'Vaishali'), ('b', 'Other')"))
    yield engine
    await engine.dispose()


async def test_migration_adds_role_and_backfills_existing_accounts_as_admin(legacy_engine):
    applied = await ensure_schema(legacy_engine)

    assert len(applied) == 1
    async with legacy_engine.connect() as conn:
        roles = {r[0]: r[1] for r in (await conn.execute(text("SELECT username, role FROM supervisors"))).all()}
    # Both pre-existing accounts could edit the timetable before roles existed.
    assert roles == {"Vaishali": "ADMIN", "Other": "ADMIN"}


async def test_migration_is_idempotent_and_does_not_re_promote(legacy_engine):
    await ensure_schema(legacy_engine)
    async with legacy_engine.begin() as conn:
        await conn.execute(text("UPDATE supervisors SET role = 'SUPERVISOR' WHERE username = 'Other'"))

    assert await ensure_schema(legacy_engine) == []

    async with legacy_engine.connect() as conn:
        role = (await conn.execute(text("SELECT role FROM supervisors WHERE username = 'Other'"))).scalar_one()
    assert role == "SUPERVISOR"


async def test_migration_skips_a_fresh_database(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'fresh.db'}")
    try:
        assert await ensure_schema(engine) == []
    finally:
        await engine.dispose()


async def test_new_supervisors_default_to_least_privilege():
    async with TestSessionLocal() as db:
        db.add(Supervisor(username="newbie"))
        await db.commit()
        user = (await db.execute(select(Supervisor).where(Supervisor.username == "newbie"))).scalar_one()
    assert user.role == "SUPERVISOR"
    assert user.is_admin is False


async def test_me_and_login_expose_the_role(client):
    admin = await make_supervisor("boss", "ADMIN", "secret-pass")
    plain = await make_supervisor("staff", "SUPERVISOR")

    me = await client.get("/api/auth/me", headers=admin["headers"])
    assert me.json()["role"] == "ADMIN"
    me = await client.get("/api/auth/me", headers=plain["headers"])
    assert me.json()["role"] == "SUPERVISOR"

    login = await client.post("/api/auth/login", json={"username": "boss", "password": "secret-pass"})
    assert login.json()["user"]["role"] == "ADMIN"


async def test_require_admin_rejects_plain_supervisor_and_allows_admin():
    from fastapi import HTTPException

    async with TestSessionLocal() as db:
        db.add_all([Supervisor(username="a", role="ADMIN"), Supervisor(username="s", role="SUPERVISOR")])
        await db.commit()
        admin = (await db.execute(select(Supervisor).where(Supervisor.username == "a"))).scalar_one()
        plain = (await db.execute(select(Supervisor).where(Supervisor.username == "s"))).scalar_one()

    assert await require_admin(admin) is admin
    with pytest.raises(HTTPException) as exc:
        await require_admin(plain)
    assert exc.value.status_code == 403


async def test_upsert_supervisor_creates_updates_and_validates():
    async with TestSessionLocal() as db:
        user, created = await upsert_supervisor(db, "meera", password="pw", full_name="Mrs. Meera")
        assert created and user.role == "SUPERVISOR"

        user, created = await upsert_supervisor(db, "meera", role="ADMIN")
        assert not created and user.role == "ADMIN"
        assert user.full_name == "Mrs. Meera"  # untouched fields are preserved

        with pytest.raises(ValueError):
            await upsert_supervisor(db, "meera", role="ROOT")
        with pytest.raises(ValueError):
            await upsert_supervisor(db, "brand-new")  # no password supplied
