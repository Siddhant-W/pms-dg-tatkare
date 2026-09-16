from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class FavoriteTeacherResponse(BaseModel):
    teacher_id: UUID
    teacher_name: str
    class_name: str | None = None
    created_at: datetime
