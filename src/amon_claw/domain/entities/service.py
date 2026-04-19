from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class Service(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    name: str
    description: Optional[str] = None
    price: float
    duration: int  # em minutos
