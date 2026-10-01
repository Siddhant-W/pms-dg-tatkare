from datetime import date

from app.models.attendance import Attendance, AttendanceStatus
from app.models.proxy import ProxyAssignment, ProxyRequirement, RequirementStatus
from app.models.teacher import Teacher
from app.models.timetable import Weekday
from app.tests.conftest import TestSessionLocal
from app.tests.helpers import make_supervisor

MONDAY = date(2026, 8, 31)
TUESDAY = date(2026, 9, 1)


async def scenario():
    """Two requirements on Monday (periods 2 and 5), one on Tuesday."""
    sup = await make_supervisor("sup", "SUPERVISOR")  # before opening the writing session below
    async with TestSessionLocal() as db:
        absent = Teacher(name="Mrs. Absent")
        cover_a = Teacher(name="Mr. Cover A")
        cover_b = Teacher(name="Mr. Cover B")
        db.add_all([absent, cover_a, cover_b])
        await db.flush()
        reqs = {}
        for key, day, weekday, period, klass, subject in (
            ("p2", MONDAY, Weekday.MONDAY, 2, "6-I", "Mathematics"),
            ("p5", MONDAY, Weekday.MONDAY, 5, "7-II", "Science"),
            ("tue", TUESDAY, Weekday.TUESDAY, 1, "8-I", "Hindi"),
        ):
            r = ProxyRequirement(date=day, weekday=weekday, period_number=period, absent_teacher_id=absent.id,
                                 class_name=klass, subject=subject, status=RequirementStatus.ASSIGNED)
            db.add(r)
            reqs[key] = r
        await db.flush()
        assignments = {}
        for key, req, proxy in (("p2", reqs["p2"], cover_a), ("p5", reqs["p5"], cover_b), ("tue", reqs["tue"], cover_a)):
            a = ProxyAssignment(requirement_id=req.id, proxy_teacher_id=proxy.id, date=req.date,
                                period_number=req.period_number, assigned_by=sup["id"])
            db.add(a)
            assignments[key] = a
        await db.commit()
        return sup, {k: a.id for k, a in assignments.items()}


async def test_lists_everything_the_page_needs_in_period_order(client):
    sup, ids = await scenario()

    resp = await client.get("/api/proxy-assignments", params={"date": MONDAY.isoformat()}, headers=sup["headers"])

    assert resp.status_code == 200
    rows = resp.json()
    assert [r["period_number"] for r in rows] == [2, 5]
    first = rows[0]
    assert first["id"] == str(ids["p2"])
    assert first["proxy_teacher_name"] == "Mr. Cover A"
    assert first["absent_teacher_name"] == "Mrs. Absent"
    assert first["class_name"] == "6-I"
    assert first["subject"] == "Mathematics"
    assert first["date"] == MONDAY.isoformat()
    assert first["weekday"] == "MONDAY"
    assert first["status"] == "ASSIGNED"
    assert first["assigned_by_name"] == "Sup"
    assert first["assigned_at"] and first["cancelled_at"] is None


async def test_only_the_requested_day_is_returned(client):
    sup, _ = await scenario()
    resp = await client.get("/api/proxy-assignments", params={"date": TUESDAY.isoformat()}, headers=sup["headers"])
    assert [r["class_name"] for r in resp.json()] == ["8-I"]
    resp = await client.get("/api/proxy-assignments", params={"date": "2026-01-01"}, headers=sup["headers"])
    assert resp.json() == []


async def test_cancelled_assignments_are_hidden_by_default_but_can_be_listed(client):
    sup, ids = await scenario()
    assert (await client.delete(f"/api/proxy-assignments/{ids['p2']}", headers=sup["headers"])).status_code == 200
    params = {"date": MONDAY.isoformat()}

    active = (await client.get("/api/proxy-assignments", params=params, headers=sup["headers"])).json()
    assert [r["period_number"] for r in active] == [5]

    cancelled = (await client.get("/api/proxy-assignments", params={**params, "status": "CANCELLED"}, headers=sup["headers"])).json()
    assert [(r["period_number"], r["status"]) for r in cancelled] == [(2, "CANCELLED")]
    assert cancelled[0]["cancelled_at"] is not None

    everything = (await client.get("/api/proxy-assignments", params={**params, "status": "ALL"}, headers=sup["headers"])).json()
    assert [(r["period_number"], r["status"]) for r in everything] == [(2, "CANCELLED"), (5, "ASSIGNED")]


async def test_requires_a_date_a_valid_status_and_authentication(client):
    sup, _ = await scenario()
    assert (await client.get("/api/proxy-assignments", headers=sup["headers"])).status_code == 422
    assert (await client.get("/api/proxy-assignments", params={"date": MONDAY.isoformat(), "status": "BOGUS"},
                             headers=sup["headers"])).status_code == 422
    assert (await client.get("/api/proxy-assignments", params={"date": MONDAY.isoformat()})).status_code == 401


async def test_single_requirement_lookup(client):
    sup, ids = await scenario()
    resp = await client.get("/api/proxy-assignments", params={"date": MONDAY.isoformat()}, headers=sup["headers"])
    req_id = resp.json()[0]["requirement_id"]

    one = await client.get(f"/api/proxy-requirements/{req_id}", headers=sup["headers"])
    assert one.status_code == 200
    body = one.json()
    assert body["class_name"] == "6-I"
    assert body["absent_teacher_name"] == "Mrs. Absent"
    assert body["assigned_proxy_teacher_name"] == "Mr. Cover A"

    missing = await client.get("/api/proxy-requirements/00000000-0000-0000-0000-000000000000", headers=sup["headers"])
    assert missing.status_code == 404
