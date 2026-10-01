from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.teacher import Teacher
from app.models.attendance import Attendance, AttendanceStatus
from app.models.timetable import TimetableEntry
from app.models.proxy import ProxyRequirement, ProxyAssignment
from app.schemas.proxy import CandidateResponse
from app.services.class_names import ClassRef, parse_class
import uuid


@dataclass
class TeachingProfile:
    """What a teacher already teaches, from their timetable (plus the class
    they are class teacher of)."""
    classes: set[ClassRef] = field(default_factory=set)
    subjects: set[str] = field(default_factory=set)


def _normalise_subject(subject: str | None) -> str | None:
    return subject.strip().lower() if subject and subject.strip() else None


def rank_candidate(
    profile: TeachingProfile,
    requirement_class: ClassRef | None,
    requirement_subject: str | None,
    proxy_count_today: int,
    teacher_name: str,
):
    """Return ``(sort_key, class_match, subject_match, reasons)`` for one candidate.

    Ranking, most important first:
      1. Teaches the class being covered, or another division of the same
         standard (a 6-II teacher for a 6-I period) - they know the syllabus
         and the students' level.
      2. Teaches the same subject - within each of those groups, subject
         specialists come first.
      3. Teaches the exact class, ahead of a same-standard teacher.
      4. Fewest proxies already taken today, to spread the load fairly.
    Name is the final tie-break so the order is deterministic.
    """
    class_match = None
    class_reason = None
    if requirement_class is not None:
        if requirement_class in profile.classes:
            class_match = "exact"
            class_reason = f"Teaches {requirement_class.label}"
        else:
            siblings = sorted(
                (c for c in profile.classes if c.same_standard(requirement_class)),
                key=lambda c: c.label,
            )
            if siblings:
                class_match = "same_standard"
                class_reason = f"Teaches {', '.join(c.label for c in siblings)} (same standard)"

    requirement_subject_key = _normalise_subject(requirement_subject)
    subject_match = requirement_subject_key is not None and requirement_subject_key in profile.subjects

    reasons = []
    if class_reason:
        reasons.append(class_reason)
    if subject_match:
        reasons.append(f"Teaches {requirement_subject.strip()}")
    reasons.append("Free this period")
    reasons.append(f"{proxy_count_today} prox{'y' if proxy_count_today == 1 else 'ies'} today")

    sort_key = (
        0 if class_match else 1,
        0 if subject_match else 1,
        0 if class_match == "exact" else 1,
        proxy_count_today,
        teacher_name.lower(),
    )
    return sort_key, class_match, subject_match, reasons


async def get_candidates(db: AsyncSession, requirement_id: uuid.UUID):
    req_stmt = select(ProxyRequirement).where(ProxyRequirement.id == requirement_id)
    req = (await db.execute(req_stmt)).scalar_one_or_none()
    if not req:
        return []

    # 1. Active teachers who are present. Attendance is "mark absent" based:
    #    everyone is present unless they have an ABSENT record for the day.
    active_teachers = (await db.execute(select(Teacher).where(Teacher.active == True))).scalars().all()
    absent_ids = set((await db.execute(
        select(Attendance.teacher_id).where(
            Attendance.date == req.date,
            Attendance.status == AttendanceStatus.ABSENT,
        )
    )).scalars().all())
    present_dict = {t.id: t for t in active_teachers if t.id not in absent_ids}

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

    eligible = [
        teacher for tid, teacher in present_dict.items()
        if tid != req.absent_teacher_id and tid not in busy_teachers and tid not in assigned_proxy_teacher_ids
    ]
    if not eligible:
        return []

    # 5. What each eligible teacher already teaches (whole week). Free periods
    #    are skipped: for them class_name is just the class-teacher label.
    teaching_stmt = select(TimetableEntry).where(
        TimetableEntry.teacher_id.in_([t.id for t in eligible]),
        TimetableEntry.is_free == False,
        TimetableEntry.is_recess == False,
    )
    profiles = {t.id: TeachingProfile() for t in eligible}
    for entry in (await db.execute(teaching_stmt)).scalars().all():
        profile = profiles[entry.teacher_id]
        parsed = parse_class(entry.class_name)
        if parsed:
            profile.classes.add(parsed)
        subject = _normalise_subject(entry.subject)
        if subject:
            profile.subjects.add(subject)
    for teacher in eligible:
        own_class = parse_class(teacher.class_name)
        if own_class:
            profiles[teacher.id].classes.add(own_class)

    requirement_class = parse_class(req.class_name)

    ranked = []
    for teacher in eligible:
        proxy_count = pa_counts.get(teacher.id, 0)
        sort_key, class_match, subject_match, reasons = rank_candidate(
            profiles[teacher.id], requirement_class, req.subject, proxy_count, teacher.name
        )
        ranked.append((sort_key, CandidateResponse(
            teacher_id=teacher.id,
            teacher_name=teacher.name,
            is_recommended=False,
            score=sort_key[0] * 1000 + sort_key[1] * 100 + sort_key[2] * 50 + proxy_count * 10,
            class_match=class_match,
            subject_match=subject_match,
            proxy_count_today=proxy_count,
            reasons=reasons,
        )))

    ranked.sort(key=lambda pair: pair[0])
    candidates = [candidate for _, candidate in ranked]
    for position, candidate in enumerate(candidates, start=1):
        candidate.rank = position
    candidates[0].is_recommended = True

    return candidates
