
import pytest

from amon_claw.domain.entities.tenant import (
    BusinessHours,
    MessagingProvider,
    Tenant,
    TenantMessagingConfig,
    TenantSettings,
)
from amon_claw.infrastructure.database.mongodb.repositories.tenant_repository import (
    TenantRepository,
)


@pytest.mark.asyncio
async def test_tenant_repository_save_with_messaging_config():
    repo = TenantRepository()

    messaging_config = TenantMessagingConfig(
        provider=MessagingProvider.evolution,
        evolution_api_url="http://localhost:8080",
        evolution_api_key="secret",
        evolution_instance_name="test-instance"
    )

    tenant = Tenant(
        name="Messaging Tenant",
        phone="5511999999999",
        business_hours={},
        messaging_config=messaging_config
    )

    saved_tenant = await repo.save(tenant)

    assert saved_tenant.messaging_config.provider == MessagingProvider.evolution
    assert saved_tenant.messaging_config.evolution_api_url == "http://localhost:8080"
    assert saved_tenant.messaging_config.evolution_api_key == "secret"

    # Retrieve from DB
    retrieved = await repo.get_by_id(tenant.id)
    assert retrieved is not None
    assert retrieved.messaging_config.provider == MessagingProvider.evolution
    assert retrieved.messaging_config.evolution_instance_name == "test-instance"

@pytest.mark.asyncio
async def test_tenant_repository_save():
    repo = TenantRepository()

    business_hours = {
        "monday": BusinessHours(open="09:00", close="18:00")
    }

    tenant = Tenant(
        name="Test Tenant",
        phone="123456789",
        business_hours=business_hours,
        settings=TenantSettings(human_in_the_loop=True)
    )

    saved_tenant = await repo.save(tenant)

    assert saved_tenant.id == tenant.id
    assert saved_tenant.name == "Test Tenant"
    assert saved_tenant.phone == "123456789"
    assert saved_tenant.settings.human_in_the_loop is True

@pytest.mark.asyncio
async def test_tenant_repository_get_by_phone():
    repo = TenantRepository()

    phone = "987654321"
    tenant = Tenant(
        name="Another Tenant",
        phone=phone,
        business_hours={
            "monday": BusinessHours(open="10:00", close="20:00")
        }
    )

    await repo.save(tenant)

    retrieved_tenant = await repo.get_by_phone(phone)

    assert retrieved_tenant is not None
    assert retrieved_tenant.id == tenant.id
    assert retrieved_tenant.phone == phone

@pytest.mark.asyncio
async def test_tenant_repository_get_by_id():
    repo = TenantRepository()

    tenant = Tenant(
        name="ID Tenant",
        phone="111222333",
        business_hours={}
    )

    await repo.save(tenant)

    retrieved_tenant = await repo.get_by_id(tenant.id)

    assert retrieved_tenant is not None
    assert retrieved_tenant.id == tenant.id

@pytest.mark.asyncio
async def test_tenant_repository_delete():
    repo = TenantRepository()

    tenant = Tenant(
        name="Delete Me",
        phone="000000000",
        business_hours={}
    )

    await repo.save(tenant)

    # Verify it exists
    assert await repo.get_by_id(tenant.id) is not None

    # Delete
    success = await repo.delete(tenant.id)
    assert success is True

    # Verify it's gone
    assert await repo.get_by_id(tenant.id) is None

@pytest.mark.asyncio
async def test_tenant_repository_admin_hash_persistence():
    repo = TenantRepository()
    
    tenant = Tenant(
        name="Hash Tenant",
        phone="5511888888888",
        business_hours={},
        admin_hash="secret_hash_789"
    )
    
    await repo.save(tenant)
    
    retrieved = await repo.get_by_id(tenant.id)
    assert retrieved is not None
    assert retrieved.admin_hash == "secret_hash_789"

@pytest.mark.asyncio
async def test_tenant_repository_get_by_phone_not_found():
    repo = TenantRepository()
    retrieved_tenant = await repo.get_by_phone("non-existent")
    assert retrieved_tenant is None
