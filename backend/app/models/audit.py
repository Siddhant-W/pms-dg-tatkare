from app.core.database import Base
from sqlalchemy import Column, String, ForeignKey, DateTime, Uuid, JSON
import uuid
from datetime import datetime, timezone

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    actor_id = Column(Uuid, ForeignKey("supervisors.id"))
    event_type = Column(String)
    entity_type = Column(String)
    entity_id = Column(Uuid)
    metadata_json = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
