from app.core.database import Base
from sqlalchemy import Column, ForeignKey, DateTime, Uuid
from datetime import datetime, timezone

class FavoriteTeacher(Base):
    __tablename__ = "favorite_teachers"
    supervisor_id = Column(Uuid, ForeignKey("supervisors.id"), primary_key=True)
    teacher_id = Column(Uuid, ForeignKey("teachers.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
