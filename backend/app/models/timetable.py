from app.core.database import Base
from sqlalchemy import Column, String, Integer, Boolean, Time, ForeignKey, Enum, UniqueConstraint, Index, Uuid
import uuid
import enum

class Weekday(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"

class TimetableEntry(Base):
    __tablename__ = "timetable_entries"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id = Column(Uuid, ForeignKey("teachers.id"))
    weekday = Column(Enum(Weekday))
    period_number = Column(Integer)
    subject = Column(String, nullable=True)
    class_name = Column(String, nullable=True)
    is_recess = Column(Boolean, default=False)
    is_free = Column(Boolean, default=False)
    time_start = Column(Time, nullable=True)
    time_end = Column(Time, nullable=True)
    
    __table_args__ = (
        UniqueConstraint("teacher_id", "weekday", "period_number"),
        Index("ix_timetable_weekday_period_teacher", "weekday", "period_number", "teacher_id")
    )
