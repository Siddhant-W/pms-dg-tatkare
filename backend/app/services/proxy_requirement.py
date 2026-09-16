from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.timetable import TimetableEntry, Weekday
from app.models.proxy import ProxyRequirement, RequirementStatus
from app.models.audit import AuditEvent
from datetime import date

async def generate_requirements(db: AsyncSession, teacher_id, d: date, supervisor_id=None):
    weekday_str = d.strftime("%A").upper()
    try:
        weekday = Weekday(weekday_str)
    except ValueError:
        return []  # Sunday or unrecognized day
    
    # Get timetable entries for the teacher on this day
    stmt = select(TimetableEntry).where(
        TimetableEntry.teacher_id == teacher_id,
        TimetableEntry.weekday == weekday,
        TimetableEntry.is_free == False,
        TimetableEntry.is_recess == False
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()
    
    requirements = []
    for entry in entries:
        # Check if already exists
        check_stmt = select(ProxyRequirement).where(
            ProxyRequirement.date == d,
            ProxyRequirement.absent_teacher_id == teacher_id,
            ProxyRequirement.period_number == entry.period_number
        )
        existing = (await db.execute(check_stmt)).scalar_one_or_none()
        if not existing:
            req = ProxyRequirement(
                date=d,
                weekday=weekday,
                period_number=entry.period_number,
                absent_teacher_id=teacher_id,
                class_name=entry.class_name,
                subject=entry.subject,
                status=RequirementStatus.PENDING
            )
            db.add(req)
            requirements.append(req)

    if requirements:
        await db.flush()
        for req in requirements:
            db.add(AuditEvent(
                actor_id=supervisor_id,
                event_type="REQUIREMENT_CREATED",
                entity_type="ProxyRequirement",
                entity_id=req.id,
                metadata_json={
                    "absent_teacher_id": str(teacher_id),
                    "period_number": req.period_number,
                    "class_name": req.class_name,
                    "subject": req.subject,
                },
            ))

    await db.commit()
    return requirements

async def remove_pending_requirements(db: AsyncSession, teacher_id, d: date):
    stmt = delete(ProxyRequirement).where(
        ProxyRequirement.date == d,
        ProxyRequirement.absent_teacher_id == teacher_id,
        ProxyRequirement.status == RequirementStatus.PENDING
    )
    await db.execute(stmt)
    await db.commit()
