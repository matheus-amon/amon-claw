import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from amon_claw.presentation.api.app import app
from amon_claw.domain.entities.tenant import MessagingProvider

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_tenant():
    mock = AsyncMock()
    mock.messaging_config.provider = MessagingProvider.twilio
    mock.messaging_config.model_dump.return_value = {"provider": "twilio"}
    return mock

@pytest.mark.asyncio
async def test_twilio_webhook(client: AsyncClient, mock_tenant):
    tenant_id = "test-tenant"
    payload = {
        "From": "whatsapp:+1234567890",
        "Body": "Hello world",
        "MessageSid": "SM12345"
    }
    
    with patch("amon_claw.infrastructure.database.mongodb.models.tenant.TenantDocument.get", return_value=mock_tenant), \
         patch("amon_claw.infrastructure.llm.agents.sdr_graph.sdr_assistant.ainvoke", return_value={"messages": [AsyncMock(type="assistant", content="Olá!")]}), \
         patch("amon_claw.presentation.api.routes.webhooks.get_messaging_client") as mock_get_client:
        
        mock_messaging_client = AsyncMock()
        mock_get_client.return_value = mock_messaging_client
        
        response = await client.post(
            f"/v1/webhooks/twilio/{tenant_id}",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        assert "xml" in response.headers["content-type"]
        assert "<Response></Response>" in response.text
        mock_messaging_client.send_text.assert_called_once()

@pytest.mark.asyncio
async def test_evolution_webhook(client: AsyncClient, mock_tenant):
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
    
    with patch("amon_claw.infrastructure.database.mongodb.models.tenant.TenantDocument.get", return_value=mock_tenant), \
         patch("amon_claw.infrastructure.llm.agents.sdr_graph.sdr_assistant.ainvoke", return_value={"messages": [AsyncMock(type="assistant", content="Olá!")]}), \
         patch("amon_claw.presentation.api.routes.webhooks.get_messaging_client") as mock_get_client:
        
        mock_messaging_client = AsyncMock()
        mock_get_client.return_value = mock_messaging_client
        
        response = await client.post(
            f"/v1/webhooks/evolution/{tenant_id}",
            json=payload
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        mock_messaging_client.send_text.assert_called_once()

