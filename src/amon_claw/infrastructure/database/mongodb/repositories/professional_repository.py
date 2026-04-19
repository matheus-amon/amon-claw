from amon_claw.domain.entities.professional import Professional
from amon_claw.infrastructure.database.mongodb.models.professional import (
    ProfessionalDocument,
)
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository


class ProfessionalRepository(MongoRepository[Professional, ProfessionalDocument]):
    """
    MongoDB implementation of a Professional repository.
    """
    def __init__(self):
        super().__init__(ProfessionalDocument, Professional)
