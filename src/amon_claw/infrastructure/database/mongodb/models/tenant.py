from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from amon_claw.domain.entities.tenant import Tenant


class TenantDocument(Document, Tenant):
    """
    MongoDB representation of a Tenant using Beanie.
    """
    id: UUID = Field(default_factory=uuid4, alias="_id")

    class Settings:
        name = "tenants"
        indexes = ["phone"]
