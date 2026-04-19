from datetime import datetime
from typing import Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class BusinessHours(BaseModel):
    open: str
    close: str

class TenantSettings(BaseModel):
    human_in_the_loop: bool = False
    buffer_time: int = 15  # em minutos

class Tenant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    phone: str
    business_hours: Dict[str, BusinessHours]
    settings: TenantSettings = Field(default_factory=TenantSettings)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
