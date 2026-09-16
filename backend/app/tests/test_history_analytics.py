import pytest
from datetime import date
from app.models.teacher import Teacher
from app.models.supervisor import Supervisor
from app.models.timetable import TimetableEntry, Weekday
from app.models.attendance import AttendanceStatus
from app.services.attendance import mark_attendance
from app.services.proxy_assignment import assign_proxy
from app.services.history import get_history
from app.services.analytics import get_daily_stats
from app.core.exceptions import ConflictException
from app.tests.conftest import TestSessionLocal


@pytest.mark.asyncio
async def test_history_and_analytics_end_to_end():
    # History is filtered by when the audit entry was recorded (created_at),
    # which in real usage always matches the attendance/requirement date since
    # the app only ever marks attendance for "today". A fixed historical date
    # combined with today's timetable weekday keeps this deterministic.
    test_date = date.today()
    if test_date.weekday() == 6:  # Sunday: school has no classes, requirement generation is a no-op
        pytest.skip("test relies on today being a school day")
    weekday = Weekday(test_date.strftime("%A").upper())

    async with TestSessionLocal() as db:
        supe = Supervisor(username="hist_test")
        absent_teacher = Teacher(name="History Absent Teacher")
        proxy_teacher = Teacher(name="History Proxy Teacher")
        db.add_all([supe, absent_teacher, proxy_teacher])
        await db.commit()

        db.add(TimetableEntry(
            teacher_id=absent_teacher.id,
            weekday=weekday,
            period_number=2,
            subject="Science",
            class_name="6A",
            is_free=False,
        ))
        db.add(TimetableEntry(
            teacher_id=proxy_teacher.id,
            weekday=weekday,
            period_number=2,
            is_free=True,
        ))
        await db.commit()

        supe_id = supe.id
        absent_id = absent_teacher.id
        proxy_id = proxy_teacher.id

    # Mark the absent teacher ABSENT and the proxy candidate PRESENT.
    async with TestSessionLocal() as db:
        await mark_attendance(db, absent_id, test_date, AttendanceStatus.ABSENT, supe_id)
    async with TestSessionLocal() as db:
        await mark_attendance(db, proxy_id, test_date, AttendanceStatus.PRESENT, supe_id)

    # There should now be exactly one PENDING requirement for period 2.
    from sqlalchemy.future import select
    from app.models.proxy import ProxyRequirement

    async with TestSessionLocal() as db:
        req = (await db.execute(
            select(ProxyRequirement).where(ProxyRequirement.absent_teacher_id == absent_id)
        )).scalar_one()
        req_id = req.id

    async with TestSessionLocal() as db:
        await assign_proxy(db, req_id, proxy_id, supe_id)

    # A second attempt at the same requirement must be rejected and logged as
    # a prevented collision.
    async with TestSessionLocal() as db:
        with pytest.raises(ConflictException):
            await assign_proxy(db, req_id, proxy_id, supe_id)

    async with TestSessionLocal() as db:
        events = await get_history(db, test_date, None)
        event_types = [e.event_type for e in events]
        assert "ATTENDANCE_MARKED" in event_types
        assert "REQUIREMENT_CREATED" in event_types
        assert "ASSIGNMENT_CREATED" in event_types
        assert "ASSIGNMENT_COLLISION_PREVENTED" in event_types

        assignment_event = next(e for e in events if e.event_type == "ASSIGNMENT_CREATED")
        assert "History Proxy Teacher" in assignment_event.summary
        assert "6A" in assignment_event.summary

        # Filtering by the absent teacher should surface their own events.
        filtered = await get_history(db, test_date, absent_id)
        assert any(e.event_type == "ATTENDANCE_MARKED" for e in filtered)

    async with TestSessionLocal() as db:
        stats = await get_daily_stats(db, test_date)
        assert stats.absent_count >= 1
        assert stats.requirements_count >= 1
        assert stats.assigned_count >= 1
        assert stats.collision_attempts >= 1
        proxy_names = [t.teacher_name for t in stats.proxy_load_distribution]
        assert "History Proxy Teacher" in proxy_names
