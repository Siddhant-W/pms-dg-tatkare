from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.models.teacher import Teacher
from app.models.attendance import Attendance, AttendanceStatus
from app.models.audit import AuditEvent
from app.schemas.teacher import TeacherWithAttendanceResponse, TeacherCreate, TeacherUpdate, TeacherResponse
from typing import List, Optional
from datetime import date as date_type
from uuid import UUID

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

@router.post("", response_model=TeacherResponse, status_code=201)
async def create_teacher(
    data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    await db.flush()
    db.add(AuditEvent(
        actor_id=current_user.id,
        event_type="TEACHER_CREATED",
        entity_type="Teacher",
        entity_id=teacher.id,
        metadata_json={"name": teacher.name, "class_name": teacher.class_name},
    ))
    await db.commit()
    await db.refresh(teacher)
    return teacher

@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: UUID,
    data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    teacher = await db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)

    await db.flush()
    db.add(AuditEvent(
        actor_id=current_user.id,
        event_type="TEACHER_UPDATED",
        entity_type="Teacher",
        entity_id=teacher.id,
        metadata_json=update_data,
    ))
    await db.commit()
    await db.refresh(teacher)
    return teacher
