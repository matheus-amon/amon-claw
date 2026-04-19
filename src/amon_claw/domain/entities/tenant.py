from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessagingProvider(str, Enum):
    twilio = "twilio"
    evolution = "evolution"

class BusinessHours(BaseModel):
    open: str
    close: str

class TenantSettings(BaseModel):
    human_in_the_loop: bool = False
    buffer_time: int = 15  # em minutos

class TenantMessagingConfig(BaseModel):
    provider: MessagingProvider = MessagingProvider.twilio
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None
    evolution_api_url: str | None = None
    evolution_api_key: str | None = None
    evolution_instance_name: str | None = None

class Tenant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    phone: str
    admin_hash: str = Field(default="12345")
    business_hours: dict[str, BusinessHours]
    settings: TenantSettings = Field(default_factory=TenantSettings)
    messaging_config: TenantMessagingConfig = Field(default_factory=TenantMessagingConfig)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
