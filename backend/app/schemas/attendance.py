from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from app.models.attendance import AttendanceStatus

class AttendanceUpdate(BaseModel):
    status: AttendanceStatus

class AttendanceResponse(BaseModel):
    id: UUID
    teacher_id: UUID
    date: date
    status: AttendanceStatus
    marked_at: datetime
    marked_by: UUID | None
    
    model_config = ConfigDict(from_attributes=True)
