from abc import ABC, abstractmethod
from uuid import UUID


class BaseRepository[T](ABC):
    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Saves a domain entity to the persistence layer.
        If the entity already exists (based on ID), it should be updated.
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        """
        Retrieves a domain entity by its unique ID.
        """
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """
        Deletes a domain entity by its ID.
        Returns True if deleted, False otherwise.
        """
        pass
