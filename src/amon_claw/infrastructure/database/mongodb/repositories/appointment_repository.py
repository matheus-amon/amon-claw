from amon_claw.domain.entities.appointment import Appointment
from amon_claw.infrastructure.database.mongodb.models.appointment import AppointmentDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository

class AppointmentRepository(MongoRepository[Appointment, AppointmentDocument]):
    """
    MongoDB implementation of an Appointment repository.
    """
    def __init__(self):
        super().__init__(AppointmentDocument, Appointment)
