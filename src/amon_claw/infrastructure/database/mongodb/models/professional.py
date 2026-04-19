from beanie import Document
from amon_claw.domain.entities.professional import Professional

class ProfessionalDocument(Document, Professional):
    """
    MongoDB representation of a Professional using Beanie.
    """
    class Settings:
        name = "professionals"
        indexes = ["tenant_id"]
