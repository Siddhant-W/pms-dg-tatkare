from app.core.database import Base
from sqlalchemy import Column, String, DateTime, Uuid
import uuid
from datetime import datetime, timezone

class Supervisor(Base):
    __tablename__ = "supervisors"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
