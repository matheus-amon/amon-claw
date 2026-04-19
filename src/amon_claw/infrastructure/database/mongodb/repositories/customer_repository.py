from uuid import UUID

from amon_claw.domain.entities.customer import Customer
from amon_claw.infrastructure.database.mongodb.models.customer import CustomerDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository


class CustomerRepository(MongoRepository[Customer, CustomerDocument]):
    """
    MongoDB implementation of a Customer repository.
    """
    def __init__(self):
        super().__init__(CustomerDocument, Customer)

    async def get_by_phone(self, tenant_id: UUID, phone: str) -> Customer | None:
        """
        Retrieves a customer by its unique phone number within a tenant.
        """
        doc = await self.document_model.find_one(
            CustomerDocument.tenant_id == tenant_id,
            CustomerDocument.phone == phone
        )
        if doc:
            return self.entity_class(**doc.model_dump())
        return None
