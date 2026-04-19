from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from amon_claw.domain.entities.appointment import Appointment


class AppointmentDocument(Document, Appointment):
    """
    MongoDB representation of an Appointment using Beanie.
    """
    id: UUID = Field(default_factory=uuid4, alias="_id")

    class Settings:
        name = "appointments"
        indexes = [
            IndexModel([("tenant_id", ASCENDING), ("start_time", ASCENDING)]),
            "professional_id"
        ]
