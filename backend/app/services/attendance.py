from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.attendance import Attendance, AttendanceStatus
from app.models.audit import AuditEvent
from app.models.teacher import Teacher
from app.services.proxy_requirement import generate_requirements, remove_pending_requirements
from datetime import date
from uuid import UUID, uuid4

async def mark_attendance(db: AsyncSession, teacher_id: UUID, d: date, status: AttendanceStatus, supervisor_id: UUID):
    stmt = select(Attendance).where(Attendance.teacher_id == teacher_id, Attendance.date == d)
    result = await db.execute(stmt)
    attendance = result.scalar_one_or_none()
    
    was_absent = False
    if attendance:
        if attendance.status == AttendanceStatus.ABSENT:
            was_absent = True
        attendance.status = status
        attendance.marked_by = supervisor_id
    else:
        attendance = Attendance(
            teacher_id=teacher_id,
            date=d,
            status=status,
            marked_by=supervisor_id
        )
        db.add(attendance)
    
    # Flush first so attendance.id is assigned before using it in audit
    await db.flush()
        
    audit = AuditEvent(
        actor_id=supervisor_id,
        event_type="ATTENDANCE_MARKED",
        entity_type="Attendance",
        entity_id=attendance.id,
        metadata_json={"teacher_id": str(teacher_id), "date": str(d), "status": status.value}
    )
    db.add(audit)
    
    if status == AttendanceStatus.ABSENT:
        await generate_requirements(db, teacher_id, d, supervisor_id)
    elif status == AttendanceStatus.PRESENT and was_absent:
        await remove_pending_requirements(db, teacher_id, d)
        
    await db.commit()
    await db.refresh(attendance)
    return attendance

async def get_attendance_summary(db: AsyncSession, d: date):
    stmt = select(Attendance.status, func.count(Attendance.id)).where(Attendance.date == d).group_by(Attendance.status)
    result = await db.execute(stmt)
    counts = dict(result.all())
    
    total_stmt = select(func.count(Teacher.id)).where(Teacher.active == True)
    total = (await db.execute(total_stmt)).scalar() or 0
    
    present = counts.get(AttendanceStatus.PRESENT, 0)
    absent = counts.get(AttendanceStatus.ABSENT, 0)
    not_marked = total - present - absent
    
    return {
        "present": present,
        "absent": absent,
        "not_marked": not_marked,
        "total": total
    }
