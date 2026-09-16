from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.schemas.attendance import AttendanceUpdate, AttendanceResponse
from app.services.attendance import mark_attendance, get_attendance_summary
from datetime import date
from uuid import UUID

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.get("/summary")
async def get_summary(
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    return await get_attendance_summary(db, date)

@router.put("/{teacher_id}", response_model=AttendanceResponse)
async def update_attendance(
    teacher_id: UUID,
    date: date = Query(...),
    data: AttendanceUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    return await mark_attendance(db, teacher_id, date, data.status, current_user.id)
