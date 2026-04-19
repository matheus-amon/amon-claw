from uuid import UUID, uuid4
from pydantic import Field
from beanie import Document
from amon_claw.domain.entities.service import Service

class ServiceDocument(Document, Service):
    """
    MongoDB representation of a Service using Beanie.
    """
    id: UUID = Field(default_factory=uuid4, alias="_id")

    class Settings:
        name = "services"
        indexes = ["tenant_id"]
