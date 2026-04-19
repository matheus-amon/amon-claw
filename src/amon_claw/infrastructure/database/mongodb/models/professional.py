from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field

from amon_claw.domain.entities.professional import Professional


class ProfessionalDocument(Document, Professional):
    """
    MongoDB representation of a Professional using Beanie.
    """
    id: UUID = Field(default_factory=uuid4, alias="_id")

    class Settings:
        name = "professionals"
        indexes = ["tenant_id"]
