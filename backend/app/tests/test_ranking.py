"""Proxy ranking: class/standard affinity first, then same subject, then load.

Scenario used throughout: Mrs. Absent teaches Mathematics to 6-I on Monday
period 3 and is away, so 6-I / Mathematics / period 3 needs cover.
"""
from datetime import date

import pytest

from app.models.attendance import Attendance, AttendanceStatus
from app.models.proxy import ProxyAssignment, ProxyRequirement, RequirementStatus
from app.models.supervisor import Supervisor
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.services.availability import get_candidates
from app.tests.conftest import TestSessionLocal
from app.tests.helpers import make_supervisor

MONDAY = date(2026, 8, 31)


async def build_scenario(teachers: dict[str, dict]):
    """Create the absent teacher, a pending requirement and the given candidates.

    ``teachers`` maps a name to ``{"teaches": [(subject, class), ...],
    "class_name": ..., "free_entries": [...], "absent": bool, "busy": bool}``.
    Every candidate is free in period 3 unless ``busy``.
    """
    async with TestSessionLocal() as db:
        supe = Supervisor(username="sup")
        absent = Teacher(name="Mrs. Absent", class_name="Class VI-1")
        db.add_all([supe, absent])
        await db.flush()
        db.add(Attendance(teacher_id=absent.id, date=MONDAY, status=AttendanceStatus.ABSENT, marked_by=supe.id))
        db.add(TimetableEntry(teacher_id=absent.id, weekday=Weekday.MONDAY, period_number=3,
                              subject="Mathematics", class_name="6-I", is_free=False))
        req = ProxyRequirement(date=MONDAY, weekday=Weekday.MONDAY, period_number=3, absent_teacher_id=absent.id,
                               class_name="6-I", subject="Mathematics", status=RequirementStatus.PENDING)
        db.add(req)

        ids = {}
        for name, spec in teachers.items():
            t = Teacher(name=name, class_name=spec.get("class_name"))
            db.add(t)
            await db.flush()
            ids[name] = t.id
            # Taught on other days/periods, so they don't clash with period 3 on Monday.
            for i, (subject, klass) in enumerate(spec.get("teaches", [])):
                db.add(TimetableEntry(teacher_id=t.id, weekday=Weekday.TUESDAY, period_number=i + 1,
                                      subject=subject, class_name=klass, is_free=False))
            for i, klass in enumerate(spec.get("free_entries", [])):
                db.add(TimetableEntry(teacher_id=t.id, weekday=Weekday.WEDNESDAY, period_number=i + 1,
                                      class_name=klass, is_free=True))
            if spec.get("busy"):
                db.add(TimetableEntry(teacher_id=t.id, weekday=Weekday.MONDAY, period_number=3,
                                      subject="English", class_name="9-I", is_free=False))
            if spec.get("absent"):
                db.add(Attendance(teacher_id=t.id, date=MONDAY, status=AttendanceStatus.ABSENT, marked_by=supe.id))
        await db.commit()
        return req.id, ids


async def ranked_names(req_id):
    async with TestSessionLocal() as db:
        return [(c.teacher_name, c) for c in await get_candidates(db, req_id)]


async def test_same_standard_teacher_beats_unrelated_and_same_subject_breaks_ties():
    req_id, _ = await build_scenario({
        "Unrelated Maths": {"teaches": [("Mathematics", "7-I")]},                       # right subject, wrong class
        "Sibling Science": {"teaches": [("Science", "6-II")]},                           # 6-II, wrong subject
        "Sibling Maths": {"teaches": [("Mathematics", "6-II")]},                         # 6-II AND Mathematics
        "Nobody": {"teaches": [("Drawing", "9-I")]},
    })

    result = await ranked_names(req_id)
    names = [n for n, _ in result]

    # Class affinity outranks subject: the 6-II Science teacher is ahead of the
    # unrelated Maths teacher. Within the affinity group, subject decides.
    assert names == ["Sibling Maths", "Sibling Science", "Unrelated Maths", "Nobody"]
    assert [c.rank for _, c in result] == [1, 2, 3, 4]
    assert [c.is_recommended for _, c in result] == [True, False, False, False]


async def test_exact_class_teacher_ranks_above_same_standard_when_subject_equal():
    req_id, _ = await build_scenario({
        "Sibling Science": {"teaches": [("Science", "6-II")]},
        "Exact English": {"teaches": [("English", "6-I")]},
    })
    names = [n for n, _ in await ranked_names(req_id)]
    assert names == ["Exact English", "Sibling Science"]


async def test_reasons_and_match_fields_explain_the_ranking():
    req_id, _ = await build_scenario({
        "Sibling Maths": {"teaches": [("Mathematics", "6-II")]},
        "Unrelated": {"teaches": [("Drawing", "9-I")]},
    })
    result = dict(await ranked_names(req_id))

    best = result["Sibling Maths"]
    assert best.class_match == "same_standard"
    assert best.subject_match is True
    assert best.reasons[0] == "Teaches 6-II (same standard)"
    assert "Teaches Mathematics" in best.reasons
    assert "Free this period" in best.reasons
    assert best.reasons[-1] == "0 proxies today"

    other = result["Unrelated"]
    assert other.class_match is None
    assert other.subject_match is False
    assert not any(r.startswith("Teaches") for r in other.reasons)


async def test_proxy_load_breaks_ties_between_equally_matched_teachers():
    req_id, ids = await build_scenario({
        "Aaa Busy Day": {"teaches": [("Mathematics", "6-II")]},
        "Zzz Quiet Day": {"teaches": [("Mathematics", "6-II")]},
    })
    # Aaa already covers another absence earlier in the day.
    async with TestSessionLocal() as db:
        other_absent = Teacher(name="Other Absent", active=False)
        db.add(other_absent)
        await db.flush()
        other_req = ProxyRequirement(date=MONDAY, weekday=Weekday.MONDAY, period_number=1,
                                     absent_teacher_id=other_absent.id, class_name="8-I", subject="Hindi",
                                     status=RequirementStatus.ASSIGNED)
        db.add(other_req)
        await db.flush()
        db.add(ProxyAssignment(requirement_id=other_req.id, proxy_teacher_id=ids["Aaa Busy Day"],
                               date=MONDAY, period_number=1))
        await db.commit()

    result = await ranked_names(req_id)
    # Same affinity and subject, so the lighter load wins even though "Aaa" sorts first alphabetically.
    assert [n for n, _ in result] == ["Zzz Quiet Day", "Aaa Busy Day"]
    assert dict(result)["Aaa Busy Day"].proxy_count_today == 1
    assert "1 proxy today" in dict(result)["Aaa Busy Day"].reasons


async def test_hard_constraints_still_exclude_the_best_matches():
    req_id, ids = await build_scenario({
        "Absent Sibling": {"teaches": [("Mathematics", "6-II")], "absent": True},
        "Busy Sibling": {"teaches": [("Mathematics", "6-II")], "busy": True},
        "Taken Sibling": {"teaches": [("Mathematics", "6-II")]},
        "Fallback": {"teaches": [("Drawing", "9-I")]},
    })
    # Taken Sibling is already covering a different class in this very period.
    async with TestSessionLocal() as db:
        elsewhere = Teacher(name="Elsewhere Absent", active=False)
        db.add(elsewhere)
        await db.flush()
        other_req = ProxyRequirement(date=MONDAY, weekday=Weekday.MONDAY, period_number=3,
                                     absent_teacher_id=elsewhere.id, class_name="8-I", subject="Hindi",
                                     status=RequirementStatus.ASSIGNED)
        db.add(other_req)
        await db.flush()
        db.add(ProxyAssignment(requirement_id=other_req.id, proxy_teacher_id=ids["Taken Sibling"],
                               date=MONDAY, period_number=3))
        await db.commit()

    names = [n for n, _ in await ranked_names(req_id)]
    assert names == ["Fallback"]


async def test_class_teacher_assignment_counts_as_teaching_that_class():
    req_id, _ = await build_scenario({
        # No timetable entries at all, but is class teacher of 6-II ("Class VI-2" spelling).
        "Class Teacher": {"class_name": "Class VI-2"},
        "Unrelated": {"teaches": [("Mathematics", "9-I")]},
    })
    result = await ranked_names(req_id)
    assert [n for n, _ in result] == ["Class Teacher", "Unrelated"]
    assert result[0][1].class_match == "same_standard"


async def test_free_period_class_labels_do_not_count_as_teaching():
    req_id, _ = await build_scenario({
        # Free-period rows carry the class-teacher label but nothing is taught.
        "Free Only": {"free_entries": ["6-II", "6-II"]},
        "Real Match": {"teaches": [("Science", "6-II")]},
    })
    result = dict(await ranked_names(req_id))
    assert result["Free Only"].class_match is None
    assert result["Real Match"].class_match == "same_standard"


async def test_requirement_without_a_parsable_class_or_subject_still_ranks_by_load():
    async with TestSessionLocal() as db:
        db.add(Supervisor(username="sup"))
        absent = Teacher(name="Absent")
        a, b = Teacher(name="A teacher"), Teacher(name="B teacher")
        db.add_all([absent, a, b])
        await db.flush()
        db.add(Attendance(teacher_id=absent.id, date=MONDAY, status=AttendanceStatus.ABSENT))
        req = ProxyRequirement(date=MONDAY, weekday=Weekday.MONDAY, period_number=3, absent_teacher_id=absent.id,
                               class_name="Assembly", subject=None, status=RequirementStatus.PENDING)
        db.add(req)
        await db.commit()
        req_id = req.id

    result = await ranked_names(req_id)
    assert [n for n, _ in result] == ["A teacher", "B teacher"]
    assert all(c.class_match is None and c.subject_match is False for _, c in result)


async def test_candidates_endpoint_exposes_ranking_fields(client):
    req_id, _ = await build_scenario({"Sibling Maths": {"teaches": [("Mathematics", "6-II")]}})
    user = await make_supervisor("viewer", "SUPERVISOR")

    resp = await client.get(f"/api/proxy-requirements/{req_id}/candidates", headers=user["headers"])

    assert resp.status_code == 200
    first = resp.json()[0]
    assert first["rank"] == 1
    assert first["is_recommended"] is True
    assert first["class_match"] == "same_standard"
    assert first["subject_match"] is True
    assert first["proxy_count_today"] == 0
    assert first["reasons"][0] == "Teaches 6-II (same standard)"
