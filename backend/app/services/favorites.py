from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.favorites import FavoriteTeacher
from app.models.teacher import Teacher
from app.schemas.favorites import FavoriteTeacherResponse
from uuid import UUID


async def list_favorites(db: AsyncSession, supervisor_id: UUID) -> list[FavoriteTeacherResponse]:
    stmt = select(FavoriteTeacher, Teacher).join(
        Teacher, Teacher.id == FavoriteTeacher.teacher_id
    ).where(FavoriteTeacher.supervisor_id == supervisor_id).order_by(FavoriteTeacher.created_at.desc())
    rows = (await db.execute(stmt)).all()
    return [
        FavoriteTeacherResponse(
            teacher_id=fav.teacher_id,
            teacher_name=teacher.name,
            class_name=teacher.class_name,
            created_at=fav.created_at,
        )
        for fav, teacher in rows
    ]


async def add_favorite(db: AsyncSession, supervisor_id: UUID, teacher_id: UUID) -> None:
    # Idempotent: favoriting an already-favorited teacher is a no-op, not an error.
    existing = (await db.execute(
        select(FavoriteTeacher).where(
            FavoriteTeacher.supervisor_id == supervisor_id, FavoriteTeacher.teacher_id == teacher_id
        )
    )).scalar_one_or_none()
    if existing:
        return
    db.add(FavoriteTeacher(supervisor_id=supervisor_id, teacher_id=teacher_id))
    await db.commit()


async def remove_favorite(db: AsyncSession, supervisor_id: UUID, teacher_id: UUID) -> None:
    existing = (await db.execute(
        select(FavoriteTeacher).where(
            FavoriteTeacher.supervisor_id == supervisor_id, FavoriteTeacher.teacher_id == teacher_id
        )
    )).scalar_one_or_none()
    if not existing:
        return
    await db.delete(existing)
    await db.commit()
