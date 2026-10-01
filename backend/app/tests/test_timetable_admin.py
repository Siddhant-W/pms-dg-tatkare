"""Admin-only timetable and teacher editing, with validation."""
import pytest
from sqlalchemy import func
from sqlalchemy.future import select

from app.models.audit import AuditEvent
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.tests.conftest import TestSessionLocal
from app.tests.helpers import make_supervisor


@pytest.fixture
async def admin():
    return await make_supervisor("admin", "ADMIN")


@pytest.fixture
async def staff():
    return await make_supervisor("staff", "SUPERVISOR")


async def add_teacher(name="Mrs. Rane", **kwargs) -> Teacher:
    async with TestSessionLocal() as db:
        teacher = Teacher(name=name, **kwargs)
        db.add(teacher)
        await db.commit()
        return teacher


async def add_lesson(teacher, weekday=Weekday.MONDAY, period=1, subject="Mathematics", klass="6-I", free=False):
    async with TestSessionLocal() as db:
        entry = TimetableEntry(teacher_id=teacher.id, weekday=weekday, period_number=period,
                               subject=None if free else subject, class_name=None if free else klass, is_free=free)
        db.add(entry)
        await db.commit()
        return entry


def upsert_url(teacher, weekday="MONDAY", period=1):
    return f"/api/timetable/{teacher.id}/{weekday}/{period}"


LESSON = {"subject": "Mathematics", "class_name": "6-I"}


# --- permissions -----------------------------------------------------------

async def test_non_admins_cannot_edit_the_timetable_or_teachers(client, staff):
    teacher = await add_teacher()
    entry = await add_lesson(teacher)

    calls = [
        client.put(upsert_url(teacher), json=LESSON, headers=staff["headers"]),
        client.put(f"/api/timetable/entries/{entry.id}", json={"subject": "Hindi"}, headers=staff["headers"]),
        client.delete(f"/api/timetable/entries/{entry.id}", headers=staff["headers"]),
        client.post("/api/teachers", json={"name": "New Person"}, headers=staff["headers"]),
        client.put(f"/api/teachers/{teacher.id}", json={"name": "Renamed"}, headers=staff["headers"]),
    ]
    for call in calls:
        resp = await call
        assert resp.status_code == 403, resp.text
        assert resp.json()["detail"] == "Admin access required"

    async with TestSessionLocal() as db:
        unchanged = await db.get(TimetableEntry, entry.id)
        assert unchanged.subject == "Mathematics"
        assert (await db.get(Teacher, teacher.id)).name == "Mrs. Rane"


async def test_unauthenticated_requests_are_rejected(client):
    teacher = await add_teacher()
    assert (await client.put(upsert_url(teacher), json=LESSON)).status_code == 401
    assert (await client.post("/api/teachers", json={"name": "X Y"})).status_code == 401


async def test_any_supervisor_can_still_view_the_timetable(client, staff):
    teacher = await add_teacher()
    await add_lesson(teacher)
    resp = await client.get("/api/timetable", params={"day": "MONDAY"}, headers=staff["headers"])
    assert resp.status_code == 200 and len(resp.json()) == 1


async def test_demoting_an_admin_takes_effect_immediately(client, admin):
    teacher = await add_teacher()
    assert (await client.put(upsert_url(teacher), json=LESSON, headers=admin["headers"])).status_code == 200

    async with TestSessionLocal() as db:
        from app.models.supervisor import Supervisor
        user = await db.get(Supervisor, admin["id"])
        user.role = "SUPERVISOR"
        await db.commit()

    # Same, still-valid token - the role is read from the database each time.
    assert (await client.put(upsert_url(teacher, period=2), json=LESSON, headers=admin["headers"])).status_code == 403


# --- field validation ------------------------------------------------------

@pytest.mark.parametrize("period", [0, 10, -1])
async def test_period_must_be_between_1_and_9(client, admin, period):
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher, period=period), json=LESSON, headers=admin["headers"])
    assert resp.status_code == 422
    assert resp.json()["detail"]["errors"][0]["field"] == "period_number"


async def test_a_lesson_needs_a_subject_and_a_class(client, admin):
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher), json={}, headers=admin["headers"])
    assert resp.status_code == 422
    fields = {e["field"] for e in resp.json()["detail"]["errors"]}
    assert fields == {"subject", "class_name"}


async def test_class_must_look_like_a_class(client, admin):
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher), json={"subject": "Hindi", "class_name": "Assembly Hall"},
                            headers=admin["headers"])
    assert resp.status_code == 422
    assert resp.json()["detail"]["errors"][0]["field"] == "class_name"


async def test_class_is_stored_in_the_canonical_spelling(client, admin):
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher), json={"subject": " Science ", "class_name": "Class VIII-2"},
                            headers=admin["headers"])
    assert resp.status_code == 200
    assert resp.json()["class_name"] == "8-II"
    assert resp.json()["subject"] == "Science"


async def test_free_periods_drop_any_subject_and_class(client, admin):
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher), json={**LESSON, "is_free": True}, headers=admin["headers"])
    assert resp.status_code == 200
    assert resp.json()["is_free"] is True
    assert resp.json()["subject"] is None and resp.json()["class_name"] is None


async def test_a_period_cannot_be_free_and_recess(client, admin):
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher), json={"is_free": True, "is_recess": True}, headers=admin["headers"])
    assert resp.status_code == 422


@pytest.mark.parametrize("times, ok", [
    ({"time_start": "09:00:00", "time_end": "09:45:00"}, True),
    ({"time_start": "09:00:00"}, False),               # only one of the pair
    ({"time_end": "09:45:00"}, False),
    ({"time_start": "10:00:00", "time_end": "09:00:00"}, False),   # backwards
    ({"time_start": "09:00:00", "time_end": "09:00:00"}, False),   # zero length
])
async def test_times_come_as_an_ordered_pair(client, admin, times, ok):
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher), json={**LESSON, **times}, headers=admin["headers"])
    assert (resp.status_code == 200) is ok, resp.text
    if not ok:
        assert resp.json()["detail"]["errors"][0]["field"] == "time_end"


async def test_unknown_teacher_is_404_and_inactive_teacher_is_rejected(client, admin):
    import uuid
    resp = await client.put(f"/api/timetable/{uuid.uuid4()}/MONDAY/1", json=LESSON, headers=admin["headers"])
    assert resp.status_code == 404

    retired = await add_teacher("Retired", active=False)
    resp = await client.put(upsert_url(retired), json=LESSON, headers=admin["headers"])
    assert resp.status_code == 422
    assert resp.json()["detail"]["errors"][0]["field"] == "teacher_id"


# --- class overlap ---------------------------------------------------------

async def test_different_subject_for_a_class_already_taught_needs_confirmation(client, admin):
    other = await add_teacher("Mr. Other")
    await add_lesson(other, subject="Science", klass="6-I")
    teacher = await add_teacher()

    resp = await client.put(upsert_url(teacher), json=LESSON, headers=admin["headers"])
    assert resp.status_code == 409
    detail = resp.json()["detail"]
    assert detail["code"] == "class_overlap"
    assert detail["conflicts"][0]["teacher_name"] == "Mr. Other"
    assert detail["conflicts"][0]["subject"] == "Science"
    async with TestSessionLocal() as db:
        assert (await db.execute(select(func.count(TimetableEntry.id)).where(TimetableEntry.teacher_id == teacher.id))).scalar() == 0

    resp = await client.put(upsert_url(teacher), json=LESSON, params={"allow_class_overlap": "true"}, headers=admin["headers"])
    assert resp.status_code == 200


async def test_same_subject_for_the_same_class_is_a_combined_session_not_a_conflict(client, admin):
    other = await add_teacher("Mr. Other")
    await add_lesson(other, subject="Mathematics", klass="Class VI-1")  # different spelling of 6-I
    teacher = await add_teacher()
    resp = await client.put(upsert_url(teacher), json=LESSON, headers=admin["headers"])
    assert resp.status_code == 200


async def test_overlap_is_per_period_and_per_class(client, admin):
    other = await add_teacher("Mr. Other")
    await add_lesson(other, subject="Science", klass="6-I", period=2)   # another period
    await add_lesson(other, subject="Science", klass="6-II", period=1)  # another class
    teacher = await add_teacher()
    assert (await client.put(upsert_url(teacher), json=LESSON, headers=admin["headers"])).status_code == 200


async def test_resaving_an_entry_unchanged_does_not_conflict_with_itself(client, admin):
    teacher = await add_teacher()
    assert (await client.put(upsert_url(teacher), json=LESSON, headers=admin["headers"])).status_code == 200
    assert (await client.put(upsert_url(teacher), json={**LESSON, "subject": "Algebra"}, headers=admin["headers"])).status_code == 200


# --- editing / moving / clearing ------------------------------------------

async def test_partial_edit_changes_only_what_was_sent(client, admin):
    teacher = await add_teacher()
    entry = await add_lesson(teacher, subject="Hindi", klass="7-I")

    resp = await client.put(f"/api/timetable/entries/{entry.id}", json={"subject": "Marathi"}, headers=admin["headers"])

    assert resp.status_code == 200
    body = resp.json()
    assert body["subject"] == "Marathi" and body["class_name"] == "7-I"
    assert body["id"] == str(entry.id)


async def test_reassigning_a_lesson_to_another_teacher_frees_the_original_slot(client, admin):
    a, b = await add_teacher("Teacher A"), await add_teacher("Teacher B")
    entry = await add_lesson(a, subject="Hindi", klass="7-I", period=3)
    await add_lesson(b, period=3, free=True)  # B's slot exists and is free

    resp = await client.put(f"/api/timetable/entries/{entry.id}", json={"teacher_id": str(b.id)}, headers=admin["headers"])

    assert resp.status_code == 200, resp.text
    assert resp.json()["teacher_id"] == str(b.id)
    async with TestSessionLocal() as db:
        source = await db.get(TimetableEntry, entry.id)
        assert source.is_free and source.subject is None and source.class_name is None
        target = (await db.execute(select(TimetableEntry).where(
            TimetableEntry.teacher_id == b.id, TimetableEntry.period_number == 3))).scalar_one()
        assert (target.subject, target.class_name, target.is_free) == ("Hindi", "7-I", False)
        # Only one teacher teaches the class in that period afterwards.
        lessons = (await db.execute(select(TimetableEntry).where(
            TimetableEntry.period_number == 3, TimetableEntry.is_free == False))).scalars().all()
        assert len(lessons) == 1


async def test_reassigning_creates_the_target_slot_if_the_grid_has_none(client, admin):
    a, b = await add_teacher("Teacher A"), await add_teacher("Teacher B")
    entry = await add_lesson(a, period=3)
    resp = await client.put(f"/api/timetable/entries/{entry.id}", json={"teacher_id": str(b.id)}, headers=admin["headers"])
    assert resp.status_code == 200
    assert resp.json()["teacher_id"] == str(b.id) and resp.json()["id"] != str(entry.id)


async def test_moving_a_lesson_onto_a_busy_teacher_is_rejected(client, admin):
    a, b = await add_teacher("Teacher A"), await add_teacher("Teacher B")
    entry = await add_lesson(a, period=3, subject="Hindi", klass="7-I")
    await add_lesson(b, period=3, subject="Science", klass="9-II")

    resp = await client.put(f"/api/timetable/entries/{entry.id}", json={"teacher_id": str(b.id)}, headers=admin["headers"])

    assert resp.status_code == 409
    detail = resp.json()["detail"]
    assert detail["code"] == "slot_occupied"
    assert "Teacher B already teaches Science to 9-II" in detail["message"]
    async with TestSessionLocal() as db:
        assert (await db.get(TimetableEntry, entry.id)).subject == "Hindi"  # nothing changed


async def test_moving_to_another_period_for_the_same_teacher(client, admin):
    teacher = await add_teacher()
    entry = await add_lesson(teacher, period=1, subject="Hindi", klass="7-I")

    resp = await client.put(f"/api/timetable/entries/{entry.id}", json={"period_number": 4, "weekday": "TUESDAY"},
                            headers=admin["headers"])

    assert resp.status_code == 200
    assert (resp.json()["period_number"], resp.json()["weekday"]) == (4, "TUESDAY")
    async with TestSessionLocal() as db:
        assert (await db.get(TimetableEntry, entry.id)).is_free is True


async def test_moving_to_an_invalid_period_is_rejected(client, admin):
    teacher = await add_teacher()
    entry = await add_lesson(teacher)
    resp = await client.put(f"/api/timetable/entries/{entry.id}", json={"period_number": 12}, headers=admin["headers"])
    assert resp.status_code == 422


async def test_clearing_a_lesson_leaves_a_free_slot_and_is_idempotent(client, admin):
    teacher = await add_teacher()
    entry = await add_lesson(teacher)

    assert (await client.delete(f"/api/timetable/entries/{entry.id}", headers=admin["headers"])).status_code == 204
    assert (await client.delete(f"/api/timetable/entries/{entry.id}", headers=admin["headers"])).status_code == 204

    async with TestSessionLocal() as db:
        cleared = await db.get(TimetableEntry, entry.id)
        assert cleared.is_free and cleared.subject is None
        events = (await db.execute(select(AuditEvent.event_type).where(AuditEvent.event_type == "TIMETABLE_ENTRY_CLEARED"))).scalars().all()
        assert len(events) == 1  # the second call did nothing


async def test_editing_an_unknown_entry_is_404(client, admin):
    import uuid
    assert (await client.put(f"/api/timetable/entries/{uuid.uuid4()}", json={"subject": "X"}, headers=admin["headers"])).status_code == 404
    assert (await client.delete(f"/api/timetable/entries/{uuid.uuid4()}", headers=admin["headers"])).status_code == 404


async def test_changes_are_recorded_in_the_audit_trail(client, admin):
    a, b = await add_teacher("Teacher A"), await add_teacher("Teacher B")
    entry = await add_lesson(a, period=2)
    await client.put(upsert_url(a, period=5), json=LESSON, headers=admin["headers"])
    await client.put(f"/api/timetable/entries/{entry.id}", json={"teacher_id": str(b.id)}, headers=admin["headers"])

    async with TestSessionLocal() as db:
        events = (await db.execute(select(AuditEvent).order_by(AuditEvent.created_at))).scalars().all()
    assert [e.event_type for e in events] == ["TIMETABLE_ENTRY_UPDATED", "TIMETABLE_ENTRY_MOVED"]
    assert events[1].actor_id == admin["id"]
    assert events[1].metadata_json["teacher_name"] == "Teacher B"


# --- teacher management ----------------------------------------------------

async def test_admin_can_add_a_teacher_and_names_are_tidied(client, admin):
    resp = await client.post("/api/teachers", json={"name": "  Mrs.   Meera   Rane ", "class_name": "Class VI-2"},
                             headers=admin["headers"])
    assert resp.status_code == 201
    assert resp.json()["name"] == "Mrs. Meera Rane"
    assert resp.json()["class_name"] == "Class VI-2"


@pytest.mark.parametrize("payload, field", [
    ({"name": " "}, "name"),
    ({"name": "A"}, "name"),
    ({"name": "x" * 81}, "name"),
    ({"name": "Valid Name", "class_name": "Staffroom"}, "class_name"),
])
async def test_teacher_validation(client, admin, payload, field):
    resp = await client.post("/api/teachers", json=payload, headers=admin["headers"])
    assert resp.status_code == 422
    assert resp.json()["detail"]["errors"][0]["field"] == field


async def test_duplicate_teacher_names_are_rejected_ignoring_case(client, admin):
    await add_teacher("Mrs. Meera Rane")
    resp = await client.post("/api/teachers", json={"name": "mrs. meera rane"}, headers=admin["headers"])
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "duplicate_teacher"


async def test_rename_deactivate_and_reactivate(client, admin):
    teacher = await add_teacher("Mrs. Old Name")
    other = await add_teacher("Mr. Taken")

    assert (await client.put(f"/api/teachers/{teacher.id}", json={"name": "Mr. Taken"}, headers=admin["headers"])).status_code == 409
    renamed = await client.put(f"/api/teachers/{teacher.id}", json={"name": "Mrs. New Name", "class_name": None},
                               headers=admin["headers"])
    assert renamed.status_code == 200 and renamed.json()["name"] == "Mrs. New Name"

    await client.put(f"/api/teachers/{teacher.id}", json={"active": False}, headers=admin["headers"])
    listed = (await client.get("/api/teachers", headers=admin["headers"])).json()
    assert [t["name"] for t in listed] == ["Mr. Taken"]
    everyone = (await client.get("/api/teachers", params={"include_inactive": "true"}, headers=admin["headers"])).json()
    assert {t["name"]: t["active"] for t in everyone} == {"Mr. Taken": True, "Mrs. New Name": False}

    # Re-activating can't create a duplicate of someone added in the meantime.
    await add_teacher("Mrs. New Name")
    resp = await client.put(f"/api/teachers/{teacher.id}", json={"active": True}, headers=admin["headers"])
    assert resp.status_code == 409


async def test_updating_an_unknown_teacher_is_404(client, admin):
    import uuid
    assert (await client.put(f"/api/teachers/{uuid.uuid4()}", json={"name": "Nobody"}, headers=admin["headers"])).status_code == 404
