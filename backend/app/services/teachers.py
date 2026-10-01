"""Teacher setup (admin only): validated create/update with an audit trail."""
import re
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import CodedConflictError, FieldValidationError
from app.models.audit import AuditEvent
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.services.class_names import parse_class


def _clean_name(raw: str) -> str:
    name = re.sub(r"\s+", " ", raw or "").strip()
    if len(name) < 2:
        raise FieldValidationError([{"field": "name", "message": "Enter the teacher's name."}])
    if len(name) > 80:
        raise FieldValidationError([{"field": "name", "message": "Name must be 80 characters or fewer."}])
    return name


def _clean_class(raw: str | None) -> str | None:
    value = (raw or "").strip()
    if not value:
        return None
    if parse_class(value) is None:
        raise FieldValidationError([{"field": "class_name", "message": "Enter a class like VI-1, 6-I or Class VIII-2."}])
    return value


async def _assert_name_free(db: AsyncSession, name: str, ignore_id: UUID | None = None) -> None:
    stmt = select(Teacher).where(func.lower(Teacher.name) == name.lower(), Teacher.active == True)
    if ignore_id is not None:
        stmt = stmt.where(Teacher.id != ignore_id)
    existing = (await db.execute(stmt)).scalars().first()
    if existing is not None:
        raise CodedConflictError(
            "duplicate_teacher",
            f"A teacher named {existing.name} already exists.",
            [{"teacher_id": str(existing.id), "teacher_name": existing.name}],
        )


async def create_teacher(db: AsyncSession, actor_id: UUID, data: TeacherCreate) -> Teacher:
    name = _clean_name(data.name)
    class_name = _clean_class(data.class_name)
    await _assert_name_free(db, name)

    teacher = Teacher(name=name, class_name=class_name, active=data.active)
    db.add(teacher)
    await db.flush()
    db.add(AuditEvent(
        actor_id=actor_id,
        event_type="TEACHER_CREATED",
        entity_type="Teacher",
        entity_id=teacher.id,
        metadata_json={"teacher_id": str(teacher.id), "name": teacher.name, "class_name": teacher.class_name},
    ))
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def update_teacher(db: AsyncSession, actor_id: UUID, teacher_id: UUID, data: TeacherUpdate) -> Teacher:
    teacher = await db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")

    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        changes["name"] = _clean_name(changes["name"] or "")
    if "class_name" in changes:
        changes["class_name"] = _clean_class(changes["class_name"])
    if "active" in changes and changes["active"] is None:
        del changes["active"]

    new_name = changes.get("name", teacher.name)
    will_be_active = changes.get("active", teacher.active)
    if will_be_active and ("name" in changes or not teacher.active):
        await _assert_name_free(db, new_name, ignore_id=teacher.id)

    before = {k: getattr(teacher, k) for k in changes}
    for field, value in changes.items():
        setattr(teacher, field, value)

    await db.flush()
    db.add(AuditEvent(
        actor_id=actor_id,
        event_type="TEACHER_UPDATED",
        entity_type="Teacher",
        entity_id=teacher.id,
        metadata_json={"teacher_id": str(teacher.id), "name": teacher.name, "changes": changes, "before": before},
    ))
    await db.commit()
    await db.refresh(teacher)
    return teacher
