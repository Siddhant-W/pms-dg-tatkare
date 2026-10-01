"""Create or update a supervisor account from the command line.

    python -m app.seeds.manage_supervisor --username Meera --full-name "Mrs. Meera Rane"
    python -m app.seeds.manage_supervisor --username Meera --role ADMIN        # promote
    python -m app.seeds.manage_supervisor --username Meera --password-prompt   # reset password

New accounts are SUPERVISOR (can mark attendance and assign proxies, but cannot
edit teachers or the timetable) unless --role ADMIN is given.
"""
import argparse
import asyncio
import getpass
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.security import get_password_hash
from app.core.database import AsyncSessionLocal, engine
from app.core.migrations import ensure_schema
from app.models.supervisor import Role, Supervisor


async def upsert_supervisor(
    db: AsyncSession,
    username: str,
    password: str | None = None,
    full_name: str | None = None,
    role: str | None = None,
) -> tuple[Supervisor, bool]:
    """Create the account, or update only the fields that were supplied.

    Returns ``(supervisor, created)``.
    """
    if role is not None and role not in {r.value for r in Role}:
        raise ValueError(f"role must be one of {[r.value for r in Role]}")

    user = (await db.execute(select(Supervisor).where(Supervisor.username == username))).scalar_one_or_none()
    created = user is None
    if created:
        if not password:
            raise ValueError("a password is required when creating a new supervisor")
        user = Supervisor(username=username, hashed_password=get_password_hash(password), full_name=full_name or username)
        db.add(user)
    else:
        if password:
            user.hashed_password = get_password_hash(password)
        if full_name:
            user.full_name = full_name

    if role is not None:
        user.role = role
    elif created:
        user.role = Role.SUPERVISOR.value

    await db.commit()
    await db.refresh(user)
    return user, created


async def _main(args: argparse.Namespace) -> int:
    await ensure_schema(engine)
    password = args.password
    if args.password_prompt:
        password = getpass.getpass("Password: ")
    async with AsyncSessionLocal() as db:
        try:
            user, created = await upsert_supervisor(db, args.username, password, args.full_name, args.role)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    print(f"{'Created' if created else 'Updated'} {user.username} (role: {user.role}).")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--username", required=True)
    parser.add_argument("--full-name")
    parser.add_argument("--role", choices=[r.value for r in Role])
    pw = parser.add_mutually_exclusive_group()
    pw.add_argument("--password", help="visible in shell history - prefer --password-prompt")
    pw.add_argument("--password-prompt", action="store_true")
    sys.exit(asyncio.run(_main(parser.parse_args())))


if __name__ == "__main__":
    main()
