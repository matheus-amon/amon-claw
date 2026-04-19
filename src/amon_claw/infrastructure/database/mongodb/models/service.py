from beanie import Document
from amon_claw.domain.entities.service import Service

class ServiceDocument(Document, Service):
    """
    MongoDB representation of a Service using Beanie.
    """
    class Settings:
        name = "services"
        indexes = ["tenant_id"]
