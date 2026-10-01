from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor, require_admin
from app.models.teacher import Teacher
from app.models.attendance import Attendance, AttendanceStatus
from app.services import teachers as teacher_service
from app.services.attendance import effective_status
from app.schemas.teacher import TeacherWithAttendanceResponse, TeacherCreate, TeacherUpdate, TeacherResponse
from typing import List, Optional
from datetime import date as date_type
from uuid import UUID

router = APIRouter(prefix="/teachers", tags=["teachers"])

@router.get("", response_model=List[TeacherWithAttendanceResponse])
async def list_teachers(
    date: Optional[date_type] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    stmt = select(Teacher).order_by(Teacher.name)
    if not include_inactive:
        stmt = stmt.where(Teacher.active == True)
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
        status = effective_status(attendance_map.get(t.id))
        output.append(TeacherWithAttendanceResponse(
            id=t.id,
            name=t.name,
            class_name=t.class_name,
            active=t.active,
            attendance_status=status
        ))
    return output

@router.post("", response_model=TeacherResponse, status_code=201)
async def create_teacher_route(
    data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(require_admin)
):
    return await teacher_service.create_teacher(db, current_user.id, data)

@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher_route(
    teacher_id: UUID,
    data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(require_admin)
):
    return await teacher_service.update_teacher(db, current_user.id, teacher_id, data)
