from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.attendance import Attendance, AttendanceStatus
from app.models.proxy import ProxyRequirement, ProxyAssignment, RequirementStatus
from app.models.audit import AuditEvent
from app.models.teacher import Teacher
from app.schemas.analytics import DailyStatsResponse, TeacherCount
from datetime import date as date_type, datetime, timedelta, timezone


async def get_daily_stats(db: AsyncSession, d: date_type) -> DailyStatsResponse:
    absent_count = (await db.execute(
        select(func.count(Attendance.id)).where(Attendance.date == d, Attendance.status == AttendanceStatus.ABSENT)
    )).scalar() or 0

    requirements_count = (await db.execute(
        select(func.count(ProxyRequirement.id)).where(ProxyRequirement.date == d)
    )).scalar() or 0

    assigned_count = (await db.execute(
        select(func.count(ProxyRequirement.id)).where(
            ProxyRequirement.date == d, ProxyRequirement.status == RequirementStatus.ASSIGNED
        )
    )).scalar() or 0

    unresolved_count = (await db.execute(
        select(func.count(ProxyRequirement.id)).where(
            ProxyRequirement.date == d, ProxyRequirement.status == RequirementStatus.UNRESOLVED
        )
    )).scalar() or 0

    # Average time from "requirement appeared" to "proxy confirmed", for
    # requirements raised on this date and still actively assigned.
    duration_stmt = select(ProxyRequirement.created_at, ProxyAssignment.assigned_at).join(
        ProxyAssignment, ProxyAssignment.requirement_id == ProxyRequirement.id
    ).where(
        ProxyRequirement.date == d,
        ProxyAssignment.cancelled_at.is_(None),
    )
    durations = (await db.execute(duration_stmt)).all()
    avg_assignment_time_seconds = None
    if durations:
        total = sum((assigned_at - created_at).total_seconds() for created_at, assigned_at in durations)
        avg_assignment_time_seconds = total / len(durations)

    start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    collision_attempts = (await db.execute(
        select(func.count(AuditEvent.id)).where(
            AuditEvent.event_type == "ASSIGNMENT_COLLISION_PREVENTED",
            AuditEvent.created_at >= start,
            AuditEvent.created_at < end,
        )
    )).scalar() or 0

    # These two are patterns over time, not a single day's snapshot, so they
    # are intentionally all-time rather than scoped to `d`.
    most_absent_stmt = select(
        Attendance.teacher_id, func.count(Attendance.id).label("cnt")
    ).where(Attendance.status == AttendanceStatus.ABSENT).group_by(Attendance.teacher_id).order_by(func.count(Attendance.id).desc()).limit(5)
    most_absent_rows = (await db.execute(most_absent_stmt)).all()

    most_assigned_stmt = select(
        ProxyAssignment.proxy_teacher_id, func.count(ProxyAssignment.id).label("cnt")
    ).where(ProxyAssignment.cancelled_at.is_(None)).group_by(ProxyAssignment.proxy_teacher_id).order_by(func.count(ProxyAssignment.id).desc()).limit(5)
    most_assigned_rows = (await db.execute(most_assigned_stmt)).all()

    load_stmt = select(
        ProxyAssignment.proxy_teacher_id, func.count(ProxyAssignment.id).label("cnt")
    ).where(
        ProxyAssignment.date == d, ProxyAssignment.cancelled_at.is_(None)
    ).group_by(ProxyAssignment.proxy_teacher_id).order_by(func.count(ProxyAssignment.id).desc())
    load_rows = (await db.execute(load_stmt)).all()

    teacher_ids = {row[0] for row in most_absent_rows + most_assigned_rows + load_rows}
    teacher_map = {}
    if teacher_ids:
        t_stmt = select(Teacher).where(Teacher.id.in_(teacher_ids))
        for t in (await db.execute(t_stmt)).scalars().all():
            teacher_map[t.id] = t.name

    def to_teacher_counts(rows):
        return [
            TeacherCount(teacher_id=str(tid), teacher_name=teacher_map.get(tid, "Unknown"), count=cnt)
            for tid, cnt in rows
        ]

    return DailyStatsResponse(
        date=d,
        absent_count=absent_count,
        requirements_count=requirements_count,
        assigned_count=assigned_count,
        unresolved_count=unresolved_count,
        avg_assignment_time_seconds=avg_assignment_time_seconds,
        collision_attempts=collision_attempts,
        most_frequently_absent_teachers=to_teacher_counts(most_absent_rows),
        most_frequently_assigned_teachers=to_teacher_counts(most_assigned_rows),
        proxy_load_distribution=to_teacher_counts(load_rows),
    )
