"""Validated timetable editing.

Everything that changes a timetable entry goes through ``save_entry`` so the
rules live in one place:

* the period must exist (1-9) and the teacher must exist and be active;
* a lesson needs a subject and a recognisable class (stored in the canonical
  ``8-II`` spelling); free periods and recess carry neither;
* start/end times come as a pair and must be in order;
* a teacher cannot have two lessons in one slot - moving a lesson onto a slot
  where that teacher already teaches is rejected;
* a class normally has one teacher per period. The school does run genuinely
  parallel sessions (combined activity periods, split language groups - the
  seeded timetable has several), so an overlap with a *different* subject is
  reported as a conflict that the admin must explicitly confirm, while the
  same subject (a combined session) is accepted silently.
"""
from dataclasses import dataclass
from datetime import time
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import CodedConflictError, FieldValidationError
from app.models.audit import AuditEvent
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.services.class_names import parse_class

MIN_PERIOD = 1
MAX_PERIOD = 9


# Aliases keep the timetable-specific names readable at the call sites.
TimetableValidationError = FieldValidationError
TimetableConflictError = CodedConflictError


@dataclass
class EntryData:
    subject: str | None
    class_name: str | None
    is_free: bool
    is_recess: bool
    time_start: time | None
    time_end: time | None


def validate_fields(period_number: int, data: EntryData) -> EntryData:
    """Check the values themselves; returns a cleaned-up copy."""
    errors: list[dict] = []

    if not MIN_PERIOD <= period_number <= MAX_PERIOD:
        errors.append({"field": "period_number", "message": f"Period must be between {MIN_PERIOD} and {MAX_PERIOD}."})

    if data.is_free and data.is_recess:
        errors.append({"field": "is_free", "message": "A period cannot be both free and recess."})

    if (data.time_start is None) != (data.time_end is None):
        errors.append({"field": "time_end", "message": "Give both a start and an end time, or neither."})
    elif data.time_start is not None and data.time_end is not None and data.time_start >= data.time_end:
        errors.append({"field": "time_end", "message": "End time must be after the start time."})

    subject = (data.subject or "").strip() or None
    class_name = (data.class_name or "").strip() or None

    if data.is_free or data.is_recess:
        # Nothing is taught, so a stray subject/class would only mislead
        # proxy ranking and requirement generation.
        subject = None
        class_name = None
    else:
        if subject is None:
            errors.append({"field": "subject", "message": "Subject is required for a lesson."})
        elif len(subject) > 60:
            errors.append({"field": "subject", "message": "Subject must be 60 characters or fewer."})

        if class_name is None:
            errors.append({"field": "class_name", "message": "Class is required for a lesson."})
        else:
            parsed = parse_class(class_name)
            if parsed is None:
                errors.append({"field": "class_name", "message": "Enter a class like 6-I, 8-II or 10-I."})
            else:
                class_name = parsed.label  # one canonical spelling in the database

    if errors:
        raise TimetableValidationError(errors, "The timetable entry is not valid.")

    return EntryData(subject, class_name, data.is_free, data.is_recess, data.time_start, data.time_end)


def _is_lesson(entry: TimetableEntry) -> bool:
    return not entry.is_free and not entry.is_recess


def _describe(entry: TimetableEntry, teacher_name: str | None) -> dict:
    return {
        "entry_id": str(entry.id),
        "teacher_id": str(entry.teacher_id),
        "teacher_name": teacher_name,
        "weekday": entry.weekday.value if entry.weekday else None,
        "period_number": entry.period_number,
        "subject": entry.subject,
        "class_name": entry.class_name,
    }


async def _find_class_overlaps(
    db: AsyncSession,
    *,
    weekday: Weekday,
    period_number: int,
    class_name: str,
    subject: str,
    teacher_id: UUID,
    ignore_entry_ids: set[UUID],
) -> list[dict]:
    """Other teachers teaching the same class at the same time, on a different subject."""
    target_class = parse_class(class_name)
    rows = (await db.execute(
        select(TimetableEntry, Teacher.name)
        .join(Teacher, Teacher.id == TimetableEntry.teacher_id)
        .where(
            TimetableEntry.weekday == weekday,
            TimetableEntry.period_number == period_number,
            TimetableEntry.teacher_id != teacher_id,
            TimetableEntry.is_free == False,
            TimetableEntry.is_recess == False,
        )
    )).all()

    overlaps = []
    for entry, teacher_name in rows:
        if entry.id in ignore_entry_ids:
            continue
        if parse_class(entry.class_name) != target_class:
            continue
        if (entry.subject or "").strip().lower() == subject.strip().lower():
            continue  # same subject: a combined session, not a clash
        overlaps.append(_describe(entry, teacher_name))
    return overlaps


async def save_entry(
    db: AsyncSession,
    actor_id: UUID,
    *,
    teacher_id: UUID,
    weekday: Weekday,
    period_number: int,
    data: EntryData,
    allow_class_overlap: bool = False,
    source: TimetableEntry | None = None,
) -> TimetableEntry:
    """Create or update the entry at (teacher, weekday, period).

    ``source`` is the entry being edited when the caller is changing an
    existing one; if the target slot differs from it, the lesson is moved and
    the source slot is left free.
    """
    teacher = await db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if not teacher.active:
        raise TimetableValidationError(
            [{"field": "teacher_id", "message": f"{teacher.name} is inactive."}],
        )

    clean = validate_fields(period_number, data)

    existing = (await db.execute(select(TimetableEntry).where(
        TimetableEntry.teacher_id == teacher_id,
        TimetableEntry.weekday == weekday,
        TimetableEntry.period_number == period_number,
    ))).scalar_one_or_none()

    moving = source is not None and (
        source.teacher_id != teacher_id or source.weekday != weekday or source.period_number != period_number
    )

    # A teacher can only be in one place at a time.
    if moving and existing is not None and _is_lesson(existing):
        raise TimetableConflictError(
            "slot_occupied",
            f"{teacher.name} already teaches {existing.subject or 'a lesson'}"
            f"{' to ' + existing.class_name if existing.class_name else ''} in that period.",
            [_describe(existing, teacher.name)],
        )

    if not clean.is_free and not clean.is_recess and not allow_class_overlap:
        ignore = {e.id for e in (source, existing) if e is not None}
        overlaps = await _find_class_overlaps(
            db, weekday=weekday, period_number=period_number, class_name=clean.class_name,
            subject=clean.subject, teacher_id=teacher_id, ignore_entry_ids=ignore,
        )
        if overlaps:
            first = overlaps[0]
            raise TimetableConflictError(
                "class_overlap",
                f"{first['teacher_name']} already teaches {first['subject']} to {clean.class_name} "
                f"in this period. Save anyway if the class is split into groups.",
                overlaps,
            )

    before = None
    if existing is None:
        entry = TimetableEntry(teacher_id=teacher_id, weekday=weekday, period_number=period_number)
        db.add(entry)
    else:
        entry = existing
        before = {"subject": entry.subject, "class_name": entry.class_name, "is_free": entry.is_free}

    entry.subject = clean.subject
    entry.class_name = clean.class_name
    entry.is_free = clean.is_free
    entry.is_recess = clean.is_recess
    entry.time_start = clean.time_start
    entry.time_end = clean.time_end

    moved_from = None
    if moving:
        moved_from = _describe(source, None)
        source.subject = None
        source.class_name = None
        source.is_free = True
        source.is_recess = False
        source.time_start = None
        source.time_end = None

    await db.flush()
    db.add(AuditEvent(
        actor_id=actor_id,
        event_type="TIMETABLE_ENTRY_MOVED" if moving else "TIMETABLE_ENTRY_UPDATED",
        entity_type="TimetableEntry",
        entity_id=entry.id,
        metadata_json={
            "teacher_id": str(teacher_id),
            "teacher_name": teacher.name,
            "weekday": weekday.value,
            "period_number": period_number,
            "subject": entry.subject,
            "class_name": entry.class_name,
            "is_free": entry.is_free,
            "before": before,
            "moved_from": moved_from,
            "overlap_confirmed": allow_class_overlap,
        },
    ))
    await db.commit()
    await db.refresh(entry)
    return entry


async def clear_entry(db: AsyncSession, actor_id: UUID, entry: TimetableEntry) -> None:
    """Remove a lesson from the timetable. The slot stays in the grid, free."""
    if entry.is_free and entry.subject is None and entry.class_name is None:
        return
    teacher = await db.get(Teacher, entry.teacher_id)
    db.add(AuditEvent(
        actor_id=actor_id,
        event_type="TIMETABLE_ENTRY_CLEARED",
        entity_type="TimetableEntry",
        entity_id=entry.id,
        metadata_json={
            "teacher_id": str(entry.teacher_id),
            "teacher_name": teacher.name if teacher else None,
            "weekday": entry.weekday.value,
            "period_number": entry.period_number,
            "subject": entry.subject,
            "class_name": entry.class_name,
        },
    ))
    entry.subject = None
    entry.class_name = None
    entry.is_free = True
    entry.is_recess = False
    entry.time_start = None
    entry.time_end = None
    await db.commit()
