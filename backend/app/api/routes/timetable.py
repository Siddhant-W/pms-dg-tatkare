from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor, require_admin
from app.models.timetable import TimetableEntry, Weekday
from app.schemas.timetable import TimetableEntryResponse, TimetableEntryUpsert, TimetableEntryUpdate
from app.services.timetable import EntryData, save_entry, clear_entry
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

# --- Editing (admin only) -------------------------------------------------
# Viewing the timetable is open to every supervisor; changing it reshapes who
# can be asked to cover which period, so it is restricted to admins.

@router.put("/{teacher_id}/{weekday}/{period_number}", response_model=TimetableEntryResponse)
async def upsert_timetable_entry(
    teacher_id: UUID,
    weekday: Weekday,
    period_number: int,
    data: TimetableEntryUpsert,
    allow_class_overlap: bool = Query(False, description="Confirm saving a lesson whose class already has a different subject in this period."),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(require_admin)
):
    """Set the lesson (or free period) for one teacher/day/period, creating it if needed."""
    return await save_entry(
        db, current_user.id,
        teacher_id=teacher_id, weekday=weekday, period_number=period_number,
        data=EntryData(data.subject, data.class_name, data.is_free, data.is_recess, data.time_start, data.time_end),
        allow_class_overlap=allow_class_overlap,
    )

@router.put("/entries/{entry_id}", response_model=TimetableEntryResponse)
async def update_timetable_entry(
    entry_id: UUID,
    data: TimetableEntryUpdate,
    allow_class_overlap: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(require_admin)
):
    """Edit an entry's teacher, class, subject, day or period.

    Only the fields sent are changed. Giving a different teacher, day or period
    moves the lesson there and leaves the original slot free.
    """
    entry = await db.get(TimetableEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Timetable entry not found")

    sent = data.model_fields_set
    def pick(name, current):
        return getattr(data, name) if name in sent else current

    # Fields that identify the slot can't be nulled out.
    return await save_entry(
        db, current_user.id,
        teacher_id=data.teacher_id or entry.teacher_id,
        weekday=data.weekday or entry.weekday,
        period_number=data.period_number if data.period_number is not None else entry.period_number,
        data=EntryData(
            subject=pick("subject", entry.subject),
            class_name=pick("class_name", entry.class_name),
            is_free=bool(pick("is_free", entry.is_free)),
            is_recess=bool(pick("is_recess", entry.is_recess)),
            time_start=pick("time_start", entry.time_start),
            time_end=pick("time_end", entry.time_end),
        ),
        allow_class_overlap=allow_class_overlap,
        source=entry,
    )

@router.delete("/entries/{entry_id}", status_code=204)
async def clear_timetable_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(require_admin)
):
    """Remove a lesson from the timetable (the slot becomes a free period)."""
    entry = await db.get(TimetableEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    await clear_entry(db, current_user.id, entry)
    return Response(status_code=204)
