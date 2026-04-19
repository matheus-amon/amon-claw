from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class AppointmentStatus(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"
    FINALIZADO = "FINALIZADO"

class Appointment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    professional_id: UUID
    customer_id: UUID
    service_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.PENDENTE
    external_calendar_id: Optional[str] = None
