from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentDeps(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    tenant_id: UUID
    customer_id: UUID
    tenant_repository: Any
    service_repository: Any
    professional_repository: Any
    appointment_repository: Any
    calendar_adapter: Any
