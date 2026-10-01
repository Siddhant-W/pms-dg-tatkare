"""Attendance is "mark absent" based: present unless an ABSENT record exists."""
from datetime import date

import pytest
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.models.attendance import Attendance, AttendanceStatus
from app.models.audit import AuditEvent
from app.models.proxy import ProxyAssignment, ProxyRequirement, RequirementStatus
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.services.attendance import mark_attendance, reset_attendance, reset_all_attendance
from app.services.proxy_assignment import assign_proxy, cancel_assignment
from app.tests.conftest import TestSessionLocal
from app.tests.helpers import make_supervisor

MONDAY = date(2026, 8, 31)
TUESDAY = date(2026, 9, 1)


async def seed_teachers():
    """Two teachers with Monday classes, plus a free substitute."""
    async with TestSessionLocal() as db:
        a = Teacher(name="Teacher A")
        b = Teacher(name="Teacher B")
        sub = Teacher(name="Substitute")
        inactive = Teacher(name="Retired", active=False)
        db.add_all([a, b, sub, inactive])
        await db.flush()
        for t, klass in ((a, "6-I"), (b, "7-I")):
            for period in (1, 2):
                db.add(TimetableEntry(teacher_id=t.id, weekday=Weekday.MONDAY, period_number=period,
                                      subject="Maths", class_name=klass, is_free=False))
        await db.commit()
        return {"a": a.id, "b": b.id, "sub": sub.id, "inactive": inactive.id}


async def test_test_database_enforces_foreign_keys():
    async with TestSessionLocal() as db:
        db.add(ProxyAssignment(requirement_id=__import__("uuid").uuid4(), proxy_teacher_id=__import__("uuid").uuid4(),
                               date=MONDAY, period_number=1))
        with pytest.raises(IntegrityError):
            await db.commit()


async def test_everyone_is_present_by_default(client):
    await seed_teachers()
    user = await make_supervisor("sup", "SUPERVISOR")

    resp = await client.get("/api/teachers", params={"date": MONDAY.isoformat()}, headers=user["headers"])

    assert resp.status_code == 200
    teachers = resp.json()
    assert len(teachers) == 3  # the inactive teacher is not listed
    assert {t["attendance_status"] for t in teachers} == {"PRESENT"}


async def test_marking_absent_and_resetting_round_trips(client):
    ids = await seed_teachers()
    user = await make_supervisor("sup", "SUPERVISOR")
    params = {"date": MONDAY.isoformat()}

    resp = await client.put(f"/api/attendance/{ids['a']}", params=params, json={"status": "ABSENT"}, headers=user["headers"])
    assert resp.status_code == 200

    teachers = {t["name"]: t["attendance_status"] for t in
                (await client.get("/api/teachers", params=params, headers=user["headers"])).json()}
    assert teachers == {"Teacher A": "ABSENT", "Teacher B": "PRESENT", "Substitute": "PRESENT"}

    resp = await client.delete(f"/api/attendance/{ids['a']}", params=params, headers=user["headers"])
    assert resp.status_code == 204

    teachers = {t["attendance_status"] for t in
                (await client.get("/api/teachers", params=params, headers=user["headers"])).json()}
    assert teachers == {"PRESENT"}


async def test_other_dates_are_unaffected(client):
    ids = await seed_teachers()
    user = await make_supervisor("sup", "SUPERVISOR")
    await client.put(f"/api/attendance/{ids['a']}", params={"date": MONDAY.isoformat()},
                     json={"status": "ABSENT"}, headers=user["headers"])

    resp = await client.get("/api/teachers", params={"date": TUESDAY.isoformat()}, headers=user["headers"])
    assert {t["attendance_status"] for t in resp.json()} == {"PRESENT"}


async def test_summary_counts_default_present_and_ignores_inactive_teachers(client):
    ids = await seed_teachers()
    user = await make_supervisor("sup", "SUPERVISOR")
    params = {"date": MONDAY.isoformat()}

    summary = (await client.get("/api/attendance/summary", params=params, headers=user["headers"])).json()
    assert summary == {"present": 3, "absent": 0, "not_marked": 0, "total": 3}

    await client.put(f"/api/attendance/{ids['a']}", params=params, json={"status": "ABSENT"}, headers=user["headers"])
    # An absence recorded for an inactive teacher must not skew today's numbers.
    async with TestSessionLocal() as db:
        db.add(Attendance(teacher_id=ids["inactive"], date=MONDAY, status=AttendanceStatus.ABSENT))
        await db.commit()

    summary = (await client.get("/api/attendance/summary", params=params, headers=user["headers"])).json()
    assert summary == {"present": 2, "absent": 1, "not_marked": 0, "total": 3}


async def test_unmarking_absent_after_a_proxy_was_cancelled_does_not_violate_foreign_keys():
    """Regression: a cancelled assignment still references its (pending again)
    requirement. Deleting the requirement used to raise on Postgres."""
    ids = await seed_teachers()
    async with TestSessionLocal() as db:
        sup = await make_supervisor("sup", "SUPERVISOR")
        await mark_attendance(db, ids["a"], MONDAY, AttendanceStatus.ABSENT, sup["id"])
        req = (await db.execute(select(ProxyRequirement).where(ProxyRequirement.period_number == 1))).scalar_one()
        assignment = await assign_proxy(db, req.id, ids["sub"], sup["id"])
        await cancel_assignment(db, assignment.id, sup["id"])

        await mark_attendance(db, ids["a"], MONDAY, AttendanceStatus.PRESENT, sup["id"])

        assert (await db.execute(select(func.count(ProxyRequirement.id)))).scalar() == 0
        assert (await db.execute(select(func.count(ProxyAssignment.id)))).scalar() == 0


async def test_unmarking_one_teacher_keeps_an_already_assigned_proxy():
    """Existing behaviour that must not change: only PENDING requirements go."""
    ids = await seed_teachers()
    async with TestSessionLocal() as db:
        sup = await make_supervisor("sup", "SUPERVISOR")
        await mark_attendance(db, ids["a"], MONDAY, AttendanceStatus.ABSENT, sup["id"])
        reqs = (await db.execute(select(ProxyRequirement).order_by(ProxyRequirement.period_number))).scalars().all()
        await assign_proxy(db, reqs[0].id, ids["sub"], sup["id"])

        await reset_attendance(db, ids["a"], MONDAY, sup["id"])

        remaining = (await db.execute(select(ProxyRequirement))).scalars().all()
        assert [(r.period_number, r.status) for r in remaining] == [(1, RequirementStatus.ASSIGNED)]


async def test_mark_all_present_clears_absences_requirements_and_assignments(client):
    ids = await seed_teachers()
    user = await make_supervisor("sup", "SUPERVISOR")
    params = {"date": MONDAY.isoformat()}
    for key in ("a", "b"):
        await client.put(f"/api/attendance/{ids[key]}", params=params, json={"status": "ABSENT"}, headers=user["headers"])

    reqs = (await client.get("/api/proxy-requirements", params=params, headers=user["headers"])).json()
    assert len(reqs) == 4
    first = next(r for r in reqs if r["period_number"] == 1 and r["absent_teacher_name"] == "Teacher A")
    resp = await client.post("/api/proxy-assignments", json={"requirement_id": first["id"], "proxy_teacher_id": str(ids["sub"])},
                             headers=user["headers"])
    assert resp.status_code == 200

    resp = await client.delete("/api/attendance", params=params, headers=user["headers"])

    assert resp.status_code == 200
    assert resp.json() == {"date": MONDAY.isoformat(), "cleared_absences": 2,
                           "removed_requirements": 4, "cancelled_assignments": 1}
    teachers = (await client.get("/api/teachers", params=params, headers=user["headers"])).json()
    assert {t["attendance_status"] for t in teachers} == {"PRESENT"}
    assert (await client.get("/api/proxy-requirements", params=params, headers=user["headers"])).json() == []

    async with TestSessionLocal() as db:
        assert (await db.execute(select(func.count(ProxyAssignment.id)))).scalar() == 0
        events = (await db.execute(select(AuditEvent.event_type))).scalars().all()
        assert "ATTENDANCE_RESET_ALL" in events
        assert "ASSIGNMENT_CANCELLED" in events


async def test_mark_all_present_only_touches_the_requested_date(client):
    ids = await seed_teachers()
    user = await make_supervisor("sup", "SUPERVISOR")
    for day in (MONDAY, TUESDAY):
        await client.put(f"/api/attendance/{ids['a']}", params={"date": day.isoformat()},
                         json={"status": "ABSENT"}, headers=user["headers"])

    await client.delete("/api/attendance", params={"date": MONDAY.isoformat()}, headers=user["headers"])

    tuesday = (await client.get("/api/teachers", params={"date": TUESDAY.isoformat()}, headers=user["headers"])).json()
    assert {t["name"]: t["attendance_status"] for t in tuesday}["Teacher A"] == "ABSENT"


async def test_mark_all_present_on_a_clean_day_is_a_harmless_noop(client):
    await seed_teachers()
    user = await make_supervisor("sup", "SUPERVISOR")

    resp = await client.delete("/api/attendance", params={"date": MONDAY.isoformat()}, headers=user["headers"])

    assert resp.status_code == 200
    assert resp.json()["cleared_absences"] == 0
    assert resp.json()["removed_requirements"] == 0


async def test_attendance_endpoints_require_authentication(client):
    assert (await client.delete("/api/attendance", params={"date": MONDAY.isoformat()})).status_code == 401
