from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.schemas.history import HistoryEventResponse
from app.services.history import get_history
from datetime import date
from typing import List
from uuid import UUID

router = APIRouter(prefix="/history", tags=["history"])

@router.get("", response_model=List[HistoryEventResponse])
async def list_history(
    date: date | None = Query(None),
    teacher_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    return await get_history(db, date, teacher_id)
