from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Any

class HistoryEventResponse(BaseModel):
    id: UUID
    event_type: str
    entity_type: str
    entity_id: UUID | None
    metadata: dict[str, Any] = {}
    created_at: datetime
    actor_name: str | None = None
    summary: str
