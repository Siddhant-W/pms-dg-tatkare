from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from app.models.proxy import RequirementStatus
from app.models.timetable import Weekday

class ProxyRequirementResponse(BaseModel):
    id: UUID
    date: date
    weekday: Weekday
    period_number: int
    absent_teacher_id: UUID
    absent_teacher_name: str | None = None
    class_name: str
    subject: str | None
    status: RequirementStatus
    created_at: datetime
    assigned_proxy_teacher_id: UUID | None = None
    assigned_proxy_teacher_name: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ProxyAssignmentResponse(BaseModel):
    id: UUID
    requirement_id: UUID
    proxy_teacher_id: UUID
    assigned_at: datetime
    assigned_by: UUID | None
    cancelled_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)

class CandidateResponse(BaseModel):
    teacher_id: UUID
    teacher_name: str
    is_recommended: bool
    score: int = 0
    reasons: list[str] = []
