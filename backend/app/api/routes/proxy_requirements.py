from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.models.proxy import ProxyRequirement, ProxyAssignment
from app.models.teacher import Teacher
from app.schemas.proxy import ProxyRequirementResponse, CandidateResponse
from app.services.availability import get_candidates
from datetime import date
from typing import List
from uuid import UUID

router = APIRouter(prefix="/proxy-requirements", tags=["proxy-requirements"])

@router.get("", response_model=List[ProxyRequirementResponse])
async def list_requirements(
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    stmt = select(ProxyRequirement).where(ProxyRequirement.date == date).order_by(ProxyRequirement.period_number)
    result = await db.execute(stmt)
    requirements = result.scalars().all()

    # Fetch teacher names for each requirement
    teacher_ids = list({r.absent_teacher_id for r in requirements})
    teacher_map = {}
    if teacher_ids:
        t_stmt = select(Teacher).where(Teacher.id.in_(teacher_ids))
        t_result = await db.execute(t_stmt)
        for t in t_result.scalars().all():
            teacher_map[t.id] = t.name

    # Active assignments for these requirements, so an ASSIGNED requirement can
    # show who is covering it without a separate round trip per card.
    requirement_ids = [r.id for r in requirements]
    assignment_map = {}
    if requirement_ids:
        a_stmt = select(ProxyAssignment, Teacher).join(
            Teacher, Teacher.id == ProxyAssignment.proxy_teacher_id
        ).where(
            ProxyAssignment.requirement_id.in_(requirement_ids),
            ProxyAssignment.cancelled_at.is_(None),
        )
        a_result = await db.execute(a_stmt)
        for assignment, teacher in a_result.all():
            assignment_map[assignment.requirement_id] = teacher

    output = []
    for r in requirements:
        proxy_teacher = assignment_map.get(r.id)
        resp = ProxyRequirementResponse(
            id=r.id,
            date=r.date,
            weekday=r.weekday,
            period_number=r.period_number,
            absent_teacher_id=r.absent_teacher_id,
            absent_teacher_name=teacher_map.get(r.absent_teacher_id),
            class_name=r.class_name,
            subject=r.subject,
            status=r.status,
            created_at=r.created_at,
            assigned_proxy_teacher_id=proxy_teacher.id if proxy_teacher else None,
            assigned_proxy_teacher_name=proxy_teacher.name if proxy_teacher else None,
        )
        output.append(resp)
    return output

@router.get("/{id}/candidates", response_model=List[CandidateResponse])
async def requirement_candidates(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    return await get_candidates(db, id)


@router.get("/{id}", response_model=ProxyRequirementResponse)
async def get_requirement(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    """One requirement, so the candidate screen can show what is being covered."""
    requirement = await db.get(ProxyRequirement, id)
    if requirement is None:
        raise HTTPException(status_code=404, detail="Proxy requirement not found")
    absent = await db.get(Teacher, requirement.absent_teacher_id)
    stmt = select(Teacher).join(
        ProxyAssignment, ProxyAssignment.proxy_teacher_id == Teacher.id
    ).where(
        ProxyAssignment.requirement_id == requirement.id,
        ProxyAssignment.cancelled_at.is_(None),
    )
    proxy = (await db.execute(stmt)).scalars().first()
    return ProxyRequirementResponse(
        id=requirement.id,
        date=requirement.date,
        weekday=requirement.weekday,
        period_number=requirement.period_number,
        absent_teacher_id=requirement.absent_teacher_id,
        absent_teacher_name=absent.name if absent else None,
        class_name=requirement.class_name,
        subject=requirement.subject,
        status=requirement.status,
        created_at=requirement.created_at,
        assigned_proxy_teacher_id=proxy.id if proxy else None,
        assigned_proxy_teacher_name=proxy.name if proxy else None,
    )
