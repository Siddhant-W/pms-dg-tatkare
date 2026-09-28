from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import time
from app.models.timetable import Weekday

class TimetableEntryBase(BaseModel):
    teacher_id: UUID
    weekday: Weekday
    period_number: int
    subject: str | None = None
    class_name: str | None = None
    is_recess: bool = False
    is_free: bool = False
    time_start: time | None = None
    time_end: time | None = None

class TimetableEntryResponse(TimetableEntryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

class TimetableEntryUpsert(BaseModel):
    subject: str | None = None
    class_name: str | None = None
    is_recess: bool = False
    is_free: bool = False
    time_start: time | None = None
    time_end: time | None = None
