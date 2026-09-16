from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.audit import AuditEvent
from app.models.supervisor import Supervisor
from app.models.teacher import Teacher
from app.models.proxy import ProxyRequirement
from app.schemas.history import HistoryEventResponse
from datetime import date as date_type, datetime, timedelta, timezone
from uuid import UUID


def _build_summary(event: AuditEvent, teacher_map: dict, requirement_map: dict) -> str:
    meta = event.metadata_json or {}

    def teacher_name(id_str: str | None) -> str:
        if not id_str:
            return "Unknown teacher"
        try:
            return teacher_map.get(UUID(id_str), "Unknown teacher")
        except ValueError:
            return "Unknown teacher"

    if event.event_type == "ATTENDANCE_MARKED":
        return f"{teacher_name(meta.get('teacher_id'))} marked {meta.get('status', '')}"

    if event.event_type == "REQUIREMENT_CREATED":
        return (
            f"Proxy needed: {meta.get('class_name', '')} · Period {meta.get('period_number', '?')} "
            f"({teacher_name(meta.get('absent_teacher_id'))} absent)"
        )

    if event.event_type == "ASSIGNMENT_CREATED":
        req = requirement_map.get(str(meta.get("requirement_id")))
        proxy_name = teacher_name(meta.get("proxy_teacher_id"))
        if req:
            return f"{proxy_name} assigned to cover {req.class_name} · Period {req.period_number}"
        return f"{proxy_name} assigned to a proxy requirement"

    if event.event_type == "ASSIGNMENT_CANCELLED":
        req = requirement_map.get(str(meta.get("requirement_id")))
        if req:
            return f"Assignment cancelled for {req.class_name} · Period {req.period_number}"
        return "Assignment cancelled"

    if event.event_type == "ASSIGNMENT_COLLISION_PREVENTED":
        proxy_name = teacher_name(meta.get("proxy_teacher_id"))
        return f"Blocked double-booking: {proxy_name} was already assigned for this period"

    return event.event_type.replace("_", " ").title()


async def get_history(db: AsyncSession, d: date_type | None, teacher_id: UUID | None) -> list[HistoryEventResponse]:
    stmt = select(AuditEvent).order_by(AuditEvent.created_at.desc())
    if d:
        start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        stmt = stmt.where(AuditEvent.created_at >= start, AuditEvent.created_at < end)

    events = (await db.execute(stmt)).scalars().all()

    if teacher_id:
        tid = str(teacher_id)
        events = [
            e for e in events
            if tid in {
                (e.metadata_json or {}).get("teacher_id"),
                (e.metadata_json or {}).get("absent_teacher_id"),
                (e.metadata_json or {}).get("proxy_teacher_id"),
            }
        ]

    if not events:
        return []

    actor_ids = {e.actor_id for e in events if e.actor_id}
    actor_map = {}
    if actor_ids:
        a_stmt = select(Supervisor).where(Supervisor.id.in_(actor_ids))
        for s in (await db.execute(a_stmt)).scalars().all():
            actor_map[s.id] = s.full_name or s.username

    teacher_ids: set[UUID] = set()
    requirement_ids: set[str] = set()
    for e in events:
        meta = e.metadata_json or {}
        for key in ("teacher_id", "absent_teacher_id", "proxy_teacher_id"):
            val = meta.get(key)
            if val:
                try:
                    teacher_ids.add(UUID(val))
                except ValueError:
                    pass
        if meta.get("requirement_id"):
            requirement_ids.add(meta["requirement_id"])
        if e.entity_type == "ProxyRequirement":
            requirement_ids.add(str(e.entity_id))

    teacher_map = {}
    if teacher_ids:
        t_stmt = select(Teacher).where(Teacher.id.in_(teacher_ids))
        for t in (await db.execute(t_stmt)).scalars().all():
            teacher_map[t.id] = t.name

    requirement_map = {}
    if requirement_ids:
        valid_ids = []
        for rid in requirement_ids:
            try:
                valid_ids.append(UUID(rid))
            except ValueError:
                pass
        if valid_ids:
            r_stmt = select(ProxyRequirement).where(ProxyRequirement.id.in_(valid_ids))
            for r in (await db.execute(r_stmt)).scalars().all():
                requirement_map[str(r.id)] = r

    output = []
    for e in events:
        output.append(HistoryEventResponse(
            id=e.id,
            event_type=e.event_type,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            metadata=e.metadata_json or {},
            created_at=e.created_at,
            actor_name=actor_map.get(e.actor_id) if e.actor_id else None,
            summary=_build_summary(e, teacher_map, requirement_map),
        ))
    return output
