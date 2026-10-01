import pytest
import pytest_asyncio
import asyncio
import os
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import get_db, Base
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.models.attendance import Attendance, AttendanceStatus
from app.models.proxy import ProxyRequirement, ProxyAssignment
from app.models.supervisor import Supervisor

TEST_DB_FILE = "test_pms.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"
test_engine = create_async_engine(TEST_DB_URL, echo=False)


@event.listens_for(test_engine.sync_engine, "connect")
def _enforce_foreign_keys(dbapi_connection, _):
    # SQLite ignores foreign keys unless asked; production Postgres never does.
    # Without this, tests pass on code that would raise IntegrityError in prod.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    # httpx >= 0.28 removed the `app=` shortcut; ASGITransport is the
    # supported way to drive the app in-process.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
