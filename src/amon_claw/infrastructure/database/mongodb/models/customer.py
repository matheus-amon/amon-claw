from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from amon_claw.domain.entities.customer import Customer


class CustomerDocument(Document, Customer):
    """
    MongoDB representation of a Customer using Beanie.
    """
    id: UUID = Field(default_factory=uuid4, alias="_id")

    class Settings:
        name = "customers"
        indexes = [
            IndexModel(
                [("tenant_id", ASCENDING), ("phone", ASCENDING)],
                unique=True
            )
        ]
