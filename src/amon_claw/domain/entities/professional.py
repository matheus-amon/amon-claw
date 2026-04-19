from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Professional(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    name: str
    calendar_id: str  # ID do Google Calendar
    services: list[UUID] = Field(default_factory=list)
