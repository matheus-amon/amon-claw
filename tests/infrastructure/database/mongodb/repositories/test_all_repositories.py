from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from amon_claw.domain.entities.appointment import Appointment
from amon_claw.domain.entities.customer import Customer
from amon_claw.domain.entities.professional import Professional
from amon_claw.domain.entities.service import Service
from amon_claw.infrastructure.database.mongodb.repositories import (
    AppointmentRepository,
    CustomerRepository,
    ProfessionalRepository,
    ServiceRepository,
)


@pytest.mark.asyncio
async def test_professional_repository_crud():
    repo = ProfessionalRepository()
    tenant_id = uuid4()
    prof = Professional(
        tenant_id=tenant_id,
        name="John Doe",
        calendar_id="cal_123",
        services=[]
    )

    # Create
    saved_prof = await repo.save(prof)
    assert saved_prof.id == prof.id
    assert saved_prof.name == "John Doe"

    # Read
    found_prof = await repo.get_by_id(prof.id)
    assert found_prof is not None
    assert found_prof.name == "John Doe"

    # Update
    saved_prof.name = "John Updated"
    updated_prof = await repo.save(saved_prof)
    assert updated_prof.name == "John Updated"

    # Delete
    deleted = await repo.delete(prof.id)
    assert deleted is True
    assert await repo.get_by_id(prof.id) is None

@pytest.mark.asyncio
async def test_service_repository_crud():
    repo = ServiceRepository()
    tenant_id = uuid4()
    service = Service(
        tenant_id=tenant_id,
        name="Haircut",
        description="Standard haircut",
        price=30.0,
        duration=30
    )

    saved = await repo.save(service)
    assert saved.id == service.id

    found = await repo.get_by_id(service.id)
    assert found.name == "Haircut"

    await repo.delete(service.id)
    assert await repo.get_by_id(service.id) is None

@pytest.mark.asyncio
async def test_customer_repository_crud_and_get_by_phone():
    repo = CustomerRepository()
    tenant_id = uuid4()
    phone = "+5511999999999"
    customer = Customer(
        tenant_id=tenant_id,
        name="Client Name",
        phone=phone
    )

    await repo.save(customer)

    # Test get_by_phone
    found = await repo.get_by_phone(tenant_id, phone)
    assert found is not None
    assert found.name == "Client Name"

    # Test with wrong tenant
    assert await repo.get_by_phone(uuid4(), phone) is None

    # Test with wrong phone
    assert await repo.get_by_phone(tenant_id, "+000") is None

@pytest.mark.asyncio
async def test_appointment_repository_crud():
    repo = AppointmentRepository()
    tenant_id = uuid4()
    appointment = Appointment(
        tenant_id=tenant_id,
        professional_id=uuid4(),
        customer_id=uuid4(),
        service_id=uuid4(),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=30),
        status="PENDENTE"
    )

    saved = await repo.save(appointment)
    assert saved.id == appointment.id

    found = await repo.get_by_id(appointment.id)
    assert found is not None
    assert found.status == "PENDENTE"

    await repo.delete(appointment.id)
    assert await repo.get_by_id(appointment.id) is None
