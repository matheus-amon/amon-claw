from abc import ABC, abstractmethod
from uuid import UUID


class IBrain(ABC):
    @abstractmethod
    async def process_message(
        self, tenant_id: UUID, customer_id: UUID, message: str
    ) -> str:
        """Process a message and return the SDR's response."""
        pass
