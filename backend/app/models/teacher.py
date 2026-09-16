from app.core.database import Base
from sqlalchemy import Column, String, Boolean, DateTime, Uuid
import uuid
from datetime import datetime, timezone

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String)
    class_name = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
