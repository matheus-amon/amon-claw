from beanie import Document
from amon_claw.domain.entities.tenant import Tenant

class TenantDocument(Document, Tenant):
    """
    MongoDB representation of a Tenant using Beanie.
    """
    class Settings:
        name = "tenants"
        indexes = ["phone"]
