import pytest
from datetime import date
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.models.attendance import Attendance, AttendanceStatus
from app.models.proxy import ProxyRequirement, ProxyAssignment, RequirementStatus
from app.models.supervisor import Supervisor
from app.services.availability import get_candidates
from app.tests.conftest import TestSessionLocal

@pytest.mark.asyncio
async def test_availability_five_hard_constraints():
    async with TestSessionLocal() as db:
        supe = Supervisor(username="Vaishali")
        # Teachers
        t_absent1 = Teacher(name="Absent Teacher 1", class_name="Class IX-1")
        t_absent2 = Teacher(name="Absent Teacher 2", class_name="Class V-1")
        t_present_free = Teacher(name="Present & Free Teacher", class_name="Class IX-1")
        t_not_present = Teacher(name="Not Present Teacher", class_name="Class IX-1")
        t_busy = Teacher(name="Busy Teacher", class_name="Class IX-1")
        t_already_proxied = Teacher(name="Already Proxied Teacher", class_name="Class IX-1")
        t_inactive = Teacher(name="Inactive Teacher", class_name="Class IX-1", active=False)
        
        db.add_all([supe, t_absent1, t_absent2, t_present_free, t_not_present, t_busy, t_already_proxied, t_inactive])
        await db.commit()
        
        test_date = date(2026, 8, 31) # Monday
        
        # Attendance records
        db.add_all([
            Attendance(teacher_id=t_absent1.id, date=test_date, status=AttendanceStatus.ABSENT, marked_by=supe.id),
            Attendance(teacher_id=t_absent2.id, date=test_date, status=AttendanceStatus.ABSENT, marked_by=supe.id),
            Attendance(teacher_id=t_present_free.id, date=test_date, status=AttendanceStatus.PRESENT, marked_by=supe.id),
            Attendance(teacher_id=t_not_present.id, date=test_date, status=AttendanceStatus.NOT_MARKED, marked_by=supe.id),
            Attendance(teacher_id=t_busy.id, date=test_date, status=AttendanceStatus.PRESENT, marked_by=supe.id),
            Attendance(teacher_id=t_already_proxied.id, date=test_date, status=AttendanceStatus.PRESENT, marked_by=supe.id),
            Attendance(teacher_id=t_inactive.id, date=test_date, status=AttendanceStatus.PRESENT, marked_by=supe.id),
        ])
        
        # Timetable for busy teacher in period 1 Monday
        db.add(TimetableEntry(
            teacher_id=t_busy.id,
            weekday=Weekday.MONDAY,
            period_number=1,
            subject="English",
            class_name="Class VIII-1",
            is_free=False
        ))
        
        # Timetable for present & free teacher in period 1 Monday (is_free=True)
        db.add(TimetableEntry(
            teacher_id=t_present_free.id,
            weekday=Weekday.MONDAY,
            period_number=1,
            is_free=True
        ))
        
        # Requirement 1: for t_absent1 period 1
        req1 = ProxyRequirement(
            date=test_date,
            weekday=Weekday.MONDAY,
            period_number=1,
            absent_teacher_id=t_absent1.id,
            class_name="Class IX-1",
            subject="Marathi",
            status=RequirementStatus.PENDING
        )
        # Requirement 2: for t_absent2 period 1, assigned to t_already_proxied
        req2 = ProxyRequirement(
            date=test_date,
            weekday=Weekday.MONDAY,
            period_number=1,
            absent_teacher_id=t_absent2.id,
            class_name="Class V-1",
            subject="Science",
            status=RequirementStatus.ASSIGNED
        )
        db.add_all([req1, req2])
        await db.flush()
        
        db.add(ProxyAssignment(
            requirement_id=req2.id,
            proxy_teacher_id=t_already_proxied.id,
            date=test_date,
            period_number=1,
            assigned_by=supe.id
        ))
        await db.commit()
        
        req1_id = req1.id
        present_free_id = t_present_free.id
        
    async with TestSessionLocal() as db:
        candidates = await get_candidates(db, req1_id)
        
        # Only t_present_free must qualify!
        candidate_ids = [c.teacher_id for c in candidates]
        assert present_free_id in candidate_ids
        assert len(candidates) == 1
        assert candidates[0].is_recommended is True
