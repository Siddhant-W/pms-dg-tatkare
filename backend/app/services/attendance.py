from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete
from app.models.attendance import Attendance, AttendanceStatus
from app.models.audit import AuditEvent
from app.models.proxy import ProxyAssignment, ProxyRequirement
from app.models.teacher import Teacher
from app.services.proxy_requirement import generate_requirements, remove_pending_requirements
from datetime import date, datetime, timezone
from uuid import UUID


def effective_status(recorded: AttendanceStatus | None) -> AttendanceStatus:
    """Attendance is "mark absent" based: everyone is present unless an ABSENT
    record exists for the day. A missing record (or a legacy NOT_MARKED one)
    therefore means present."""
    return AttendanceStatus.ABSENT if recorded == AttendanceStatus.ABSENT else AttendanceStatus.PRESENT


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
    elif was_absent:
        await remove_pending_requirements(db, teacher_id, d)

    await db.commit()
    await db.refresh(attendance)
    return attendance

async def reset_attendance(db: AsyncSession, teacher_id: UUID, d: date, supervisor_id: UUID):
    stmt = select(Attendance).where(Attendance.teacher_id == teacher_id, Attendance.date == d)
    attendance = (await db.execute(stmt)).scalar_one_or_none()

    if not attendance:
        return  # Already present by default - nothing to do.

    was_absent = attendance.status == AttendanceStatus.ABSENT
    attendance_id = attendance.id
    await db.delete(attendance)
    await db.flush()

    db.add(AuditEvent(
        actor_id=supervisor_id,
        event_type="ATTENDANCE_RESET",
        entity_type="Attendance",
        entity_id=attendance_id,
        metadata_json={"teacher_id": str(teacher_id), "date": str(d)}
    ))

    if was_absent:
        await remove_pending_requirements(db, teacher_id, d)

    await db.commit()


async def reset_all_attendance(db: AsyncSession, d: date, supervisor_id: UUID) -> dict:
    """"Mark all present": wipe the day's attendance back to the default.

    Unlike un-marking a single teacher (which only withdraws requirements that
    are still pending), this is a deliberate start-over: every absence for the
    day is cleared along with its proxy requirements, and any proxy that had
    already been assigned is cancelled. The caller is expected to confirm first.
    """
    attendance_rows = (await db.execute(select(Attendance).where(Attendance.date == d))).scalars().all()
    absences = sum(1 for a in attendance_rows if a.status == AttendanceStatus.ABSENT)

    requirement_ids = (await db.execute(
        select(ProxyRequirement.id).where(ProxyRequirement.date == d)
    )).scalars().all()

    cancelled = 0
    if requirement_ids:
        active = (await db.execute(
            select(ProxyAssignment).where(
                ProxyAssignment.requirement_id.in_(requirement_ids),
                ProxyAssignment.cancelled_at.is_(None),
            )
        )).scalars().all()
        now = datetime.now(timezone.utc)
        for assignment in active:
            assignment.cancelled_at = now
            db.add(AuditEvent(
                actor_id=supervisor_id,
                event_type="ASSIGNMENT_CANCELLED",
                entity_type="ProxyAssignment",
                entity_id=assignment.id,
                metadata_json={"requirement_id": str(assignment.requirement_id), "reason": "attendance_reset"},
            ))
        cancelled = len(active)
        await db.flush()
        # Cancelled assignment rows reference their requirement, so they have to
        # go first; the audit trail above is what preserves the history.
        await db.execute(delete(ProxyAssignment).where(ProxyAssignment.requirement_id.in_(requirement_ids)))
        await db.execute(delete(ProxyRequirement).where(ProxyRequirement.id.in_(requirement_ids)))

    await db.execute(delete(Attendance).where(Attendance.date == d))

    db.add(AuditEvent(
        actor_id=supervisor_id,
        event_type="ATTENDANCE_RESET_ALL",
        entity_type="Attendance",
        entity_id=None,
        metadata_json={
            "date": str(d),
            "cleared_absences": absences,
            "removed_requirements": len(requirement_ids),
            "cancelled_assignments": cancelled,
        },
    ))
    await db.commit()
    return {
        "date": d,
        "cleared_absences": absences,
        "removed_requirements": len(requirement_ids),
        "cancelled_assignments": cancelled,
    }


async def get_attendance_summary(db: AsyncSession, d: date):
    total_stmt = select(func.count(Teacher.id)).where(Teacher.active == True)
    total = (await db.execute(total_stmt)).scalar() or 0

    absent_stmt = select(func.count(Attendance.id)).join(
        Teacher, Teacher.id == Attendance.teacher_id
    ).where(
        Attendance.date == d,
        Attendance.status == AttendanceStatus.ABSENT,
        Teacher.active == True,
    )
    absent = (await db.execute(absent_stmt)).scalar() or 0

    return {
        "present": total - absent,
        "absent": absent,
        # Kept so a cached older client keeps working; "not marked" no longer
        # exists now that everyone defaults to present.
        "not_marked": 0,
        "total": total
    }
