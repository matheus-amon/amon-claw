from amon_claw.domain.entities.service import Service
from amon_claw.infrastructure.database.mongodb.models.service import ServiceDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository

class ServiceRepository(MongoRepository[Service, ServiceDocument]):
    """
    MongoDB implementation of a Service repository.
    """
    def __init__(self):
        super().__init__(ServiceDocument, Service)
