from app.core.database import Base
from sqlalchemy import Column, String, DateTime, Uuid
import uuid
import enum
from datetime import datetime, timezone


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"


class Supervisor(Base):
    __tablename__ = "supervisors"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    # Plain string (not a DB enum) so the column can be added to an existing
    # production table with a simple ALTER - see app/core/migrations.py. New
    # accounts are least-privileged unless explicitly created as ADMIN.
    role = Column(String, nullable=False, default=Role.SUPERVISOR.value, server_default=Role.SUPERVISOR.value)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value
