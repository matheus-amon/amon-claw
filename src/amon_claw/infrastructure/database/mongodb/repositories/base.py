from typing import Generic, TypeVar
from uuid import UUID

from beanie import Document
from pydantic import BaseModel

from amon_claw.application.interfaces.repositories.base import BaseRepository

EntityT = TypeVar("EntityT", bound=BaseModel)
DocumentT = TypeVar("DocumentT", bound=Document)

class MongoRepository(BaseRepository[EntityT], Generic[EntityT, DocumentT]):
    """
    Generic MongoDB repository implementation using Beanie.
    Handles mapping between domain entities (Pydantic models) and Beanie documents.
    """
    def __init__(self, document_model: type[DocumentT], entity_class: type[EntityT]):
        self.document_model = document_model
        self.entity_class = entity_class

    async def save(self, entity: EntityT) -> EntityT:
        """
        Saves a domain entity using its internal Beanie Document representation.
        Handles the conversion from Entity to Document and back.
        """
        # Ensure ID is present
        entity_id = getattr(entity, 'id', None)
        if not entity_id:
             raise ValueError(f"Entity of type {type(entity)} must have an 'id' field.")

        # Try to find existing document to update, or create new
        doc = await self.document_model.get(entity_id)

        if doc:
            # Update existing document with new entity data
            # Use model_dump to update fields
            new_data = entity.model_dump()
            for key, value in new_data.items():
                setattr(doc, key, value)
            await doc.save()
        else:
            # Create new document
            doc = self.document_model(**entity.model_dump())
            await doc.insert()

        return self.entity_class(**doc.model_dump())

    async def get_by_id(self, id: UUID) -> EntityT | None:
        """
        Retrieves a domain entity by its unique ID.
        """
        doc = await self.document_model.get(id)
        if doc:
            return self.entity_class(**doc.model_dump())
        return None

    async def delete(self, id: UUID) -> bool:
        """
        Deletes a domain entity by its ID.
        """
        doc = await self.document_model.get(id)
        if doc:
            await doc.delete()
            return True
        return False
