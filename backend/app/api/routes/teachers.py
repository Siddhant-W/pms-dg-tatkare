from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.models.teacher import Teacher
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.teacher import TeacherWithAttendanceResponse
from typing import List, Optional
from datetime import date as date_type

router = APIRouter(prefix="/teachers", tags=["teachers"])

@router.get("", response_model=List[TeacherWithAttendanceResponse])
async def list_teachers(
    date: Optional[date_type] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    stmt = select(Teacher).where(Teacher.active == True).order_by(Teacher.name)
    result = await db.execute(stmt)
    teachers = result.scalars().all()

    # Fetch attendance for the given date
    attendance_map = {}
    if date:
        att_stmt = select(Attendance).where(Attendance.date == date)
        att_result = await db.execute(att_stmt)
        for att in att_result.scalars().all():
            attendance_map[att.teacher_id] = att.status

    output = []
    for t in teachers:
        status = attendance_map.get(t.id, AttendanceStatus.NOT_MARKED)
        output.append(TeacherWithAttendanceResponse(
            id=t.id,
            name=t.name,
            class_name=t.class_name,
            active=t.active,
            attendance_status=status
        ))
    return output
