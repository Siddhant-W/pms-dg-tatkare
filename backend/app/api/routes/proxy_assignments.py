from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.schemas.proxy import ProxyAssignmentResponse
from app.services.proxy_assignment import assign_proxy, cancel_assignment
from pydantic import BaseModel
from uuid import UUID

router = APIRouter(prefix="/proxy-assignments", tags=["proxy-assignments"])

class AssignRequest(BaseModel):
    requirement_id: UUID
    proxy_teacher_id: UUID

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
