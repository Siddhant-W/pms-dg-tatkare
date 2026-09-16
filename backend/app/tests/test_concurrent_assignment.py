import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.proxy_assignment import assign_proxy, cancel_assignment
from app.core.exceptions import ConflictException
from app.models.proxy import ProxyRequirement, ProxyAssignment
from app.models.teacher import Teacher
from app.models.supervisor import Supervisor
from app.tests.conftest import TestSessionLocal
from datetime import date
from app.models.timetable import Weekday

@pytest.mark.asyncio
async def test_concurrent_assignment():
    # Setup test data directly via session
    async with TestSessionLocal() as db:
        supe = Supervisor(username="test")
        t1 = Teacher(name="Absent")
        t2 = Teacher(name="ProxyCandidate")
        db.add_all([supe, t1, t2])
        await db.commit()
        
        req = ProxyRequirement(
            date=date.today(),
            weekday=Weekday.MONDAY,
            period_number=1,
            absent_teacher_id=t1.id,
            class_name="10A"
        )
        db.add(req)
        await db.commit()
        
        supe_id = supe.id
        req_id = req.id
        proxy_id = t2.id
        
    # Attempt two concurrent assignments
    async def task():
        async with TestSessionLocal() as session:
            try:
                res = await assign_proxy(session, req_id, proxy_id, supe_id)
                return True
            except ConflictException:
                return False

    results = await asyncio.gather(task(), task())

    # Exactly one should succeed, one should fail with conflict
    assert results.count(True) == 1
    assert results.count(False) == 1


@pytest.mark.asyncio
async def test_cross_requirement_slot_race():
    """Two DIFFERENT requirements (different absent teachers, same date+period)
    concurrently assigning the SAME proxy teacher must not both succeed. This is
    the actual double-booking scenario from PRD acceptance criterion #8 - the
    same-requirement lock alone does not protect against it, only the partial
    unique index on (date, period_number, proxy_teacher_id) does.
    """
    async with TestSessionLocal() as db:
        supe = Supervisor(username="test2")
        absent1 = Teacher(name="Absent One")
        absent2 = Teacher(name="Absent Two")
        proxy = Teacher(name="Shared Proxy Candidate")
        db.add_all([supe, absent1, absent2, proxy])
        await db.commit()

        req1 = ProxyRequirement(
            date=date.today(),
            weekday=Weekday.MONDAY,
            period_number=3,
            absent_teacher_id=absent1.id,
            class_name="8A",
        )
        req2 = ProxyRequirement(
            date=date.today(),
            weekday=Weekday.MONDAY,
            period_number=3,
            absent_teacher_id=absent2.id,
            class_name="8B",
        )
        db.add_all([req1, req2])
        await db.commit()

        supe_id = supe.id
        req1_id = req1.id
        req2_id = req2.id
        proxy_id = proxy.id

    async def task(req_id):
        async with TestSessionLocal() as session:
            try:
                await assign_proxy(session, req_id, proxy_id, supe_id)
                return True
            except ConflictException:
                return False

    results = await asyncio.gather(task(req1_id), task(req2_id))

    assert results.count(True) == 1
    assert results.count(False) == 1

    async with TestSessionLocal() as db:
        active_stmt = select(ProxyAssignment).where(
            ProxyAssignment.proxy_teacher_id == proxy_id,
            ProxyAssignment.cancelled_at.is_(None),
        )
        active = (await db.execute(active_stmt)).scalars().all()
        assert len(active) == 1


@pytest.mark.asyncio
async def test_reassignment_after_cancellation():
    """A cancelled assignment must free up its requirement for a fresh
    assignment without tripping the (now partial) unique index on
    requirement_id.
    """
    async with TestSessionLocal() as db:
        supe = Supervisor(username="test3")
        absent = Teacher(name="Absent Three")
        proxy_a = Teacher(name="First Proxy")
        proxy_b = Teacher(name="Second Proxy")
        db.add_all([supe, absent, proxy_a, proxy_b])
        await db.commit()

        req = ProxyRequirement(
            date=date.today(),
            weekday=Weekday.MONDAY,
            period_number=5,
            absent_teacher_id=absent.id,
            class_name="9C",
        )
        db.add(req)
        await db.commit()

        supe_id = supe.id
        req_id = req.id
        proxy_a_id = proxy_a.id
        proxy_b_id = proxy_b.id

    async with TestSessionLocal() as db:
        first = await assign_proxy(db, req_id, proxy_a_id, supe_id)
        first_id = first.id

    async with TestSessionLocal() as db:
        await cancel_assignment(db, first_id, supe_id)

    async with TestSessionLocal() as db:
        second = await assign_proxy(db, req_id, proxy_b_id, supe_id)
        assert second.proxy_teacher_id == proxy_b_id

    async with TestSessionLocal() as db:
        stmt = select(ProxyAssignment).where(ProxyAssignment.requirement_id == req_id)
        rows = (await db.execute(stmt)).scalars().all()
        assert len(rows) == 2
        active = [r for r in rows if r.cancelled_at is None]
        assert len(active) == 1
        assert active[0].proxy_teacher_id == proxy_b_id
