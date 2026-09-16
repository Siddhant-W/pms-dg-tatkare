from app.core.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Date, DateTime, UniqueConstraint, Index, Uuid, text
import uuid
import enum
from datetime import datetime, timezone
from app.models.timetable import Weekday

class RequirementStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    UNRESOLVED = "UNRESOLVED"

class ProxyRequirement(Base):
    __tablename__ = "proxy_requirements"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    date = Column(Date)
    weekday = Column(Enum(Weekday))
    period_number = Column(Integer)
    absent_teacher_id = Column(Uuid, ForeignKey("teachers.id"))
    class_name = Column(String)
    subject = Column(String, nullable=True)
    status = Column(Enum(RequirementStatus), default=RequirementStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint("date", "absent_teacher_id", "period_number"),
    )

class ProxyAssignment(Base):
    __tablename__ = "proxy_assignments"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    requirement_id = Column(Uuid, ForeignKey("proxy_requirements.id"))
    proxy_teacher_id = Column(Uuid, ForeignKey("teachers.id"))
    # Denormalized from the requirement at assignment time. Required so a plain
    # DB-level unique index can enforce "one active proxy per (date, period,
    # teacher)" - ProxyRequirement alone has no proxy_teacher_id to key on.
    date = Column(Date, nullable=False)
    period_number = Column(Integer, nullable=False)
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    assigned_by = Column(Uuid, ForeignKey("supervisors.id"))
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        # A cancelled assignment frees up both the requirement and the slot for
        # reassignment, so uniqueness is scoped to *active* rows only (partial
        # index) rather than the whole table.
        Index(
            "uq_active_assignment_per_requirement",
            "requirement_id",
            unique=True,
            sqlite_where=text("cancelled_at IS NULL"),
            postgresql_where=text("cancelled_at IS NULL"),
        ),
        Index(
            "uq_active_assignment_per_slot",
            "date",
            "period_number",
            "proxy_teacher_id",
            unique=True,
            sqlite_where=text("cancelled_at IS NULL"),
            postgresql_where=text("cancelled_at IS NULL"),
        ),
    )
