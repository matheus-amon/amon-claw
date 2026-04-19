from .appointment import AppointmentDocument
from .customer import CustomerDocument
from .professional import ProfessionalDocument
from .service import ServiceDocument
from .tenant import TenantDocument

__all_models__ = [
    TenantDocument,
    ProfessionalDocument,
    ServiceDocument,
    CustomerDocument,
    AppointmentDocument,
]
