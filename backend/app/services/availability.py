from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from app.models.teacher import Teacher
from app.models.attendance import Attendance, AttendanceStatus
from app.models.timetable import TimetableEntry
from app.models.proxy import ProxyRequirement, ProxyAssignment
from app.schemas.proxy import CandidateResponse
import uuid

async def get_candidates(db: AsyncSession, requirement_id: uuid.UUID):
    req_stmt = select(ProxyRequirement).where(ProxyRequirement.id == requirement_id)
    req = (await db.execute(req_stmt)).scalar_one_or_none()
    if not req:
        return []

    # 1. Active Teachers Present Today
    teachers_stmt = select(Teacher).join(
        Attendance, (Attendance.teacher_id == Teacher.id) & (Attendance.date == req.date)
    ).where(
        Teacher.active == True,
        Attendance.status == AttendanceStatus.PRESENT
    )
    present_teachers = (await db.execute(teachers_stmt)).scalars().all()
    present_dict = {t.id: t for t in present_teachers}

    if not present_dict:
        return []

    # 2. Timetable for this period (to find who is free)
    tt_stmt = select(TimetableEntry).where(
        TimetableEntry.weekday == req.weekday,
        TimetableEntry.period_number == req.period_number,
        TimetableEntry.teacher_id.in_(present_dict.keys())
    )
    tt_entries = (await db.execute(tt_stmt)).scalars().all()
    busy_teachers = {entry.teacher_id for entry in tt_entries if not entry.is_free}

    # 3. Already assigned proxies for this period today
    pa_stmt = select(ProxyAssignment).join(
        ProxyRequirement, ProxyAssignment.requirement_id == ProxyRequirement.id
    ).where(
        ProxyRequirement.date == req.date,
        ProxyRequirement.period_number == req.period_number,
        ProxyAssignment.cancelled_at.is_(None),
        ProxyAssignment.proxy_teacher_id.in_(present_dict.keys())
    )
    assigned_proxies = (await db.execute(pa_stmt)).scalars().all()
    assigned_proxy_teacher_ids = {pa.proxy_teacher_id for pa in assigned_proxies}

    # 4. Proxy counts today (for ranking)
    all_pa_today_stmt = select(ProxyAssignment.proxy_teacher_id).join(
        ProxyRequirement, ProxyAssignment.requirement_id == ProxyRequirement.id
    ).where(
        ProxyRequirement.date == req.date,
        ProxyAssignment.cancelled_at.is_(None)
    )
    all_pa_today = (await db.execute(all_pa_today_stmt)).scalars().all()
    pa_counts = {}
    for pid in all_pa_today:
        pa_counts[pid] = pa_counts.get(pid, 0) + 1

    candidates = []
    for tid, teacher in present_dict.items():
        # Hard constraints
        if tid == req.absent_teacher_id: continue
        if tid in busy_teachers: continue
        if tid in assigned_proxy_teacher_ids: continue

        # Soft constraints / Ranking score (lower is better, or higher is better. Let's do lower score = better rank)
        proxy_count = pa_counts.get(tid, 0)
        score = proxy_count * 10
        same_class = teacher.class_name == req.class_name and req.class_name is not None
        if same_class:
            score -= 5

        reasons = ["Free this period"]
        reasons.append(f"{proxy_count} prox{'y' if proxy_count == 1 else 'ies'} today")
        if same_class:
            reasons.append(f"{req.class_name} experience")

        candidates.append(CandidateResponse(
            teacher_id=tid,
            teacher_name=teacher.name,
            is_recommended=False,
            score=score,
            reasons=reasons,
        ))

    candidates.sort(key=lambda x: x.score)
    if candidates:
        candidates[0].is_recommended = True

    return candidates
