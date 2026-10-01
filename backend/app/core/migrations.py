"""Tiny, idempotent schema upgrades applied at startup.

The project creates tables with ``Base.metadata.create_all`` (no Alembic
revisions exist), and ``create_all`` never alters a table that already exists.
So when a model gains a column, an already-deployed database would be missing
it and every query touching that model would fail. Each upgrade here inspects
the live schema first and only acts when the change is actually missing, so it
is safe to run on every boot.
"""
import logging

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.supervisor import Role

logger = logging.getLogger(__name__)


async def ensure_schema(engine: AsyncEngine) -> list[str]:
    """Apply any missing upgrades. Returns a description of what was applied."""
    applied: list[str] = []

    async with engine.begin() as conn:
        def _supervisor_columns(sync_conn):
            insp = inspect(sync_conn)
            if not insp.has_table("supervisors"):
                return None  # Fresh database - create_all/seed will build it correctly.
            return {c["name"] for c in insp.get_columns("supervisors")}

        columns = await conn.run_sync(_supervisor_columns)

        if columns is not None and "role" not in columns:
            if_not_exists = "IF NOT EXISTS " if conn.dialect.name == "postgresql" else ""
            await conn.execute(text(
                f"ALTER TABLE supervisors ADD COLUMN {if_not_exists}role VARCHAR NOT NULL "
                f"DEFAULT '{Role.SUPERVISOR.value}'"
            ))
            # Every account that exists at this point predates roles and could
            # already edit the timetable, so they keep that ability. Accounts
            # created afterwards default to the least-privileged role.
            await conn.execute(text(f"UPDATE supervisors SET role = '{Role.ADMIN.value}'"))
            applied.append("supervisors.role (existing accounts backfilled as ADMIN)")

    for change in applied:
        logger.info("Applied schema upgrade: %s", change)
    return applied
