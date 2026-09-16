from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models.attendance import AttendanceStatus

class TeacherBase(BaseModel):
    name: str
    class_name: str | None = None
    active: bool = True

class TeacherCreate(TeacherBase):
    pass

class TeacherResponse(TeacherBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TeacherWithAttendanceResponse(BaseModel):
    id: UUID
    name: str
    class_name: str | None = None
    active: bool
    attendance_status: AttendanceStatus = AttendanceStatus.NOT_MARKED

    model_config = ConfigDict(from_attributes=True)
