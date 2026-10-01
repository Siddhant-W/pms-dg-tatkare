from datetime import date
from typing import List, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.models.teacher import Teacher
from app.models.proxy import ProxyAssignment, ProxyRequirement
from app.api.deps import get_current_supervisor
from app.schemas.proxy import ProxyAssignmentResponse, ProxyAssignmentDetail
from app.services.proxy_assignment import assign_proxy, cancel_assignment
from pydantic import BaseModel
from uuid import UUID

router = APIRouter(prefix="/proxy-assignments", tags=["proxy-assignments"])

class AssignRequest(BaseModel):
    requirement_id: UUID
    proxy_teacher_id: UUID

@router.get("", response_model=List[ProxyAssignmentDetail])
async def list_assignments(
    date: date = Query(..., description="The day to list assignments for."),
    status: Literal["ASSIGNED", "CANCELLED", "ALL"] = Query("ASSIGNED"),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    """Who is covering whose class, for a day. Defaults to active assignments."""
    stmt = select(ProxyAssignment, ProxyRequirement).join(
        ProxyRequirement, ProxyRequirement.id == ProxyAssignment.requirement_id
    ).where(ProxyAssignment.date == date)
    if status == "ASSIGNED":
        stmt = stmt.where(ProxyAssignment.cancelled_at.is_(None))
    elif status == "CANCELLED":
        stmt = stmt.where(ProxyAssignment.cancelled_at.is_not(None))
    stmt = stmt.order_by(ProxyRequirement.period_number, ProxyAssignment.assigned_at)
    rows = (await db.execute(stmt)).all()
    if not rows:
        return []

    teacher_ids = {a.proxy_teacher_id for a, _ in rows} | {r.absent_teacher_id for _, r in rows}
    teacher_names = {t.id: t.name for t in (await db.execute(
        select(Teacher).where(Teacher.id.in_(teacher_ids))
    )).scalars().all()}
    assigner_ids = {a.assigned_by for a, _ in rows if a.assigned_by}
    assigner_names = {}
    if assigner_ids:
        assigner_names = {s.id: s.full_name or s.username for s in (await db.execute(
            select(Supervisor).where(Supervisor.id.in_(assigner_ids))
        )).scalars().all()}

    return [
        ProxyAssignmentDetail(
            id=assignment.id,
            requirement_id=requirement.id,
            date=assignment.date,
            weekday=requirement.weekday,
            period_number=assignment.period_number,
            class_name=requirement.class_name,
            subject=requirement.subject,
            absent_teacher_id=requirement.absent_teacher_id,
            absent_teacher_name=teacher_names.get(requirement.absent_teacher_id),
            proxy_teacher_id=assignment.proxy_teacher_id,
            proxy_teacher_name=teacher_names.get(assignment.proxy_teacher_id),
            status="CANCELLED" if assignment.cancelled_at else "ASSIGNED",
            assigned_at=assignment.assigned_at,
            assigned_by_name=assigner_names.get(assignment.assigned_by),
            cancelled_at=assignment.cancelled_at,
        )
        for assignment, requirement in rows
    ]

@router.post("", response_model=ProxyAssignmentResponse)
async def create_assignment(
    req: AssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    return await assign_proxy(db, req.requirement_id, req.proxy_teacher_id, current_user.id)

@router.delete("/{id}")
async def delete_assignment(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    await cancel_assignment(db, id, current_user.id)
    return {"status": "cancelled"}
