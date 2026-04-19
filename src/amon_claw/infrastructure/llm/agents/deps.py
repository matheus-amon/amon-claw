from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Any
from amon_claw.infrastructure.database.mongodb.repositories.tenant_repository import TenantRepository
from amon_claw.infrastructure.database.mongodb.repositories.service_repository import ServiceRepository
from amon_claw.infrastructure.database.mongodb.repositories.professional_repository import ProfessionalRepository
from amon_claw.infrastructure.database.mongodb.repositories.appointment_repository import AppointmentRepository

class AgentDeps(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    tenant_id: UUID
    customer_id: UUID
    tenant_repository: TenantRepository
    service_repository: ServiceRepository
    professional_repository: ProfessionalRepository
    appointment_repository: AppointmentRepository
    calendar_adapter: Any
