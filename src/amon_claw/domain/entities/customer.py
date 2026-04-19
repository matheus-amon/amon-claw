from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class Customer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    name: str
    phone: str
    history: List[UUID] = Field(default_factory=list)
