from pymongo import IndexModel, ASCENDING
from beanie import Document
from amon_claw.domain.entities.customer import Customer

class CustomerDocument(Document, Customer):
    """
    MongoDB representation of a Customer using Beanie.
    """
    class Settings:
        name = "customers"
        indexes = [
            IndexModel(
                [("tenant_id", ASCENDING), ("phone", ASCENDING)],
                unique=True
            )
        ]
