from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.models.audit import AuditEvent
from app.schemas.timetable import TimetableEntryResponse, TimetableEntryUpsert
from typing import List
from uuid import UUID

router = APIRouter(prefix="/timetable", tags=["timetable"])

@router.get("", response_model=List[TimetableEntryResponse])
async def get_timetable(
    day: Weekday | None = None,
    teacher_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    stmt = select(TimetableEntry)
    if day:
        stmt = stmt.where(TimetableEntry.weekday == day)
    if teacher_id:
        stmt = stmt.where(TimetableEntry.teacher_id == teacher_id)

    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/{teacher_id}/{weekday}/{period_number}", response_model=TimetableEntryResponse)
async def upsert_timetable_entry(
    teacher_id: UUID,
    weekday: Weekday,
    period_number: int,
    data: TimetableEntryUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    teacher = await db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    stmt = select(TimetableEntry).where(
        TimetableEntry.teacher_id == teacher_id,
        TimetableEntry.weekday == weekday,
        TimetableEntry.period_number == period_number,
    )
    entry = (await db.execute(stmt)).scalar_one_or_none()

    if entry:
        entry.subject = data.subject
        entry.class_name = data.class_name
        entry.is_recess = data.is_recess
        entry.is_free = data.is_free
        entry.time_start = data.time_start
        entry.time_end = data.time_end
    else:
        entry = TimetableEntry(
            teacher_id=teacher_id,
            weekday=weekday,
            period_number=period_number,
            **data.model_dump(),
        )
        db.add(entry)

    await db.flush()
    db.add(AuditEvent(
        actor_id=current_user.id,
        event_type="TIMETABLE_ENTRY_UPDATED",
        entity_type="TimetableEntry",
        entity_id=entry.id,
        metadata_json={
            "teacher_id": str(teacher_id),
            "weekday": weekday.value,
            "period_number": period_number,
            "subject": data.subject,
            "class_name": data.class_name,
        },
    ))
    await db.commit()
    await db.refresh(entry)
    return entry
