
from amon_claw.domain.entities.tenant import Tenant
from amon_claw.infrastructure.database.mongodb.models.tenant import TenantDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository


class TenantRepository(MongoRepository[Tenant, TenantDocument]):
    """
    MongoDB implementation of a Tenant repository.
    """
    def __init__(self):
        super().__init__(TenantDocument, Tenant)

    async def get_by_phone(self, phone: str) -> Tenant | None:
        """
        Retrieves a tenant by its unique phone number.
        """
        doc = await self.document_model.find_one(TenantDocument.phone == phone)
        if doc:
            return self.entity_class(**doc.model_dump())
        return None
