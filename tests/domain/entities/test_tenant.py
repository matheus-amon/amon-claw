from amon_claw.domain.entities.tenant import Tenant

def test_tenant_has_admin_hash_default():
    tenant = Tenant(
        name="Test Tenant",
        phone="123456789",
        business_hours={}
    )
    assert hasattr(tenant, "admin_hash")
    assert tenant.admin_hash == "12345"

def test_tenant_custom_admin_hash():
    tenant = Tenant(
        name="Test Tenant",
        phone="123456789",
        business_hours={},
        admin_hash="custom_secret"
    )
    assert tenant.admin_hash == "custom_secret"
