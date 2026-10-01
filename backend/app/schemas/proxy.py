from typing import Literal
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

class ProxyAssignmentDetail(BaseModel):
    """One proxy assignment with everything the Assigned Proxies page shows."""
    id: UUID
    requirement_id: UUID
    date: date
    weekday: Weekday
    period_number: int
    class_name: str | None = None
    subject: str | None = None
    absent_teacher_id: UUID
    absent_teacher_name: str | None = None
    proxy_teacher_id: UUID
    proxy_teacher_name: str | None = None
    # ASSIGNED while the proxy is covering the period, CANCELLED once withdrawn.
    status: Literal["ASSIGNED", "CANCELLED"]
    assigned_at: datetime
    assigned_by_name: str | None = None
    cancelled_at: datetime | None = None


class CandidateResponse(BaseModel):
    teacher_id: UUID
    teacher_name: str
    is_recommended: bool
    # Lower is better. Kept for older clients; `rank` is what the UI shows.
    score: int = 0
    rank: int = 0
    # How this teacher relates to the class being covered: they teach that exact
    # class, or another division of the same standard (e.g. 6-II for a 6-I period).
    class_match: Literal["exact", "same_standard"] | None = None
    subject_match: bool = False
    proxy_count_today: int = 0
    reasons: list[str] = []
