from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.schemas.analytics import DailyStatsResponse
from app.services.analytics import get_daily_stats
from datetime import date

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("", response_model=DailyStatsResponse)
async def analytics(
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    return await get_daily_stats(db, date)
