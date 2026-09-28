from app.core.database import Base
from app.models.supervisor import Supervisor
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.models.attendance import Attendance, AttendanceStatus
from app.models.proxy import ProxyRequirement, ProxyAssignment, RequirementStatus
from app.models.audit import AuditEvent

__all__ = [
    "Base",
    "Supervisor",
    "Teacher",
    "TimetableEntry",
    "Weekday",
    "Attendance",
    "AttendanceStatus",
    "ProxyRequirement",
    "ProxyAssignment",
    "RequirementStatus",
    "AuditEvent",
]
