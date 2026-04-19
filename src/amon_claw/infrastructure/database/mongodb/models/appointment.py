from pymongo import IndexModel, ASCENDING
from beanie import Document
from amon_claw.domain.entities.appointment import Appointment

class AppointmentDocument(Document, Appointment):
    """
    MongoDB representation of an Appointment using Beanie.
    """
    class Settings:
        name = "appointments"
        indexes = [
            IndexModel([("tenant_id", ASCENDING), ("start_time", ASCENDING)]),
            "professional_id"
        ]
