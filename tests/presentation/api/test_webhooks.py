import pytest
from httpx import AsyncClient, ASGITransport
from amon_claw.presentation.api.app import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_twilio_webhook(client: AsyncClient):
    tenant_id = "test-tenant"
    payload = {
        "From": "whatsapp:+1234567890",
        "Body": "Hello world",
        "MessageSid": "SM12345"
    }
    response = await client.post(
        f"/v1/webhooks/twilio/{tenant_id}",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert "<Response></Response>" in response.text

@pytest.mark.asyncio
async def test_evolution_webhook(client: AsyncClient):
    tenant_id = "test-tenant"
    payload = {
        "event": "messages.upsert",
        "instance": "instance-1",
        "data": {
            "key": {
                "remoteJid": "1234567890@s.whatsapp.net",
                "fromMe": False,
                "id": "12345"
            },
            "message": {
                "conversation": "Hello from Evolution"
            }
        }
    }
    response = await client.post(
        f"/v1/webhooks/evolution/{tenant_id}",
        json=payload
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
