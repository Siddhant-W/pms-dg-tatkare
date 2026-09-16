from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.models.timetable import TimetableEntry, Weekday
from app.schemas.timetable import TimetableEntryResponse
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
