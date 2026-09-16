import pytest
from datetime import date
from sqlalchemy.future import select
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.models.attendance import Attendance, AttendanceStatus
from app.models.proxy import ProxyRequirement, RequirementStatus
from app.models.supervisor import Supervisor
from app.services.attendance import mark_attendance
from app.tests.conftest import TestSessionLocal

@pytest.mark.asyncio
async def test_attendance_and_requirement_generation_flow():
    async with TestSessionLocal() as db:
        supe = Supervisor(username="Vaishali")
        teacher = Teacher(name="Mrs. Mahable A.A.", class_name="Class IX-1")
        db.add_all([supe, teacher])
        await db.commit()
        
        test_date = date(2026, 8, 31) # Monday
        
        # Add 2 scheduled periods and 1 free period for this teacher on Monday
        db.add_all([
            TimetableEntry(teacher_id=teacher.id, weekday=Weekday.MONDAY, period_number=1, subject="Marathi", class_name="Class IX-1", is_free=False),
            TimetableEntry(teacher_id=teacher.id, weekday=Weekday.MONDAY, period_number=2, is_free=True),
            TimetableEntry(teacher_id=teacher.id, weekday=Weekday.MONDAY, period_number=4, subject="Marathi", class_name="Class X-1", is_free=False),
        ])
        await db.commit()
        
        supe_id = supe.id
        teacher_id = teacher.id
        
    # 1. Mark Teacher ABSENT -> Should auto-generate exactly 2 requirements (periods 1 & 4)
    async with TestSessionLocal() as db:
        att = await mark_attendance(db, teacher_id, test_date, AttendanceStatus.ABSENT, supe_id)
        assert att.status == AttendanceStatus.ABSENT
        
        reqs = (await db.execute(select(ProxyRequirement).where(
            ProxyRequirement.date == test_date,
            ProxyRequirement.absent_teacher_id == teacher_id
        ))).scalars().all()
        
        assert len(reqs) == 2
        period_numbers = {r.period_number for r in reqs}
        assert period_numbers == {1, 4}
        assert all(r.status == RequirementStatus.PENDING for r in reqs)

    # 2. Mark Teacher PRESENT -> Should remove only PENDING requirements
    async with TestSessionLocal() as db:
        att = await mark_attendance(db, teacher_id, test_date, AttendanceStatus.PRESENT, supe_id)
        assert att.status == AttendanceStatus.PRESENT
        
        reqs_after = (await db.execute(select(ProxyRequirement).where(
            ProxyRequirement.date == test_date,
            ProxyRequirement.absent_teacher_id == teacher_id
        ))).scalars().all()
        
        assert len(reqs_after) == 0
