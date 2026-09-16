from pydantic import BaseModel
from datetime import date

class TeacherCount(BaseModel):
    teacher_id: str
    teacher_name: str
    count: int

class DailyStatsResponse(BaseModel):
    date: date
    absent_count: int
    requirements_count: int
    assigned_count: int
    unresolved_count: int
    avg_assignment_time_seconds: float | None
    collision_attempts: int
    most_frequently_absent_teachers: list[TeacherCount]
    most_frequently_assigned_teachers: list[TeacherCount]
    proxy_load_distribution: list[TeacherCount]
