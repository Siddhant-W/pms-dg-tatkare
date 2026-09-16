from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Enum, Date, DateTime, UniqueConstraint, Uuid
import uuid
import enum
from datetime import datetime, timezone

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    NOT_MARKED = "NOT_MARKED"

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id = Column(Uuid, ForeignKey("teachers.id"))
    date = Column(Date)
    status = Column(Enum(AttendanceStatus))
    marked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    marked_by = Column(Uuid, ForeignKey("supervisors.id"))
    
    __table_args__ = (
        UniqueConstraint("teacher_id", "date"),
    )
