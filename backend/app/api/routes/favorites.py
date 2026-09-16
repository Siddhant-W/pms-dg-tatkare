from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.supervisor import Supervisor
from app.api.deps import get_current_supervisor
from app.schemas.favorites import FavoriteTeacherResponse
from app.services.favorites import list_favorites, add_favorite, remove_favorite
from typing import List
from uuid import UUID

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("", response_model=List[FavoriteTeacherResponse])
async def get_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    return await list_favorites(db, current_user.id)

@router.post("/{teacher_id}", status_code=204)
async def create_favorite(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    await add_favorite(db, current_user.id, teacher_id)

@router.delete("/{teacher_id}", status_code=204)
async def delete_favorite(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Supervisor = Depends(get_current_supervisor)
):
    await remove_favorite(db, current_user.id, teacher_id)
