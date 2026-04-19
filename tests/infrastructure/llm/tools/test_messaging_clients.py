import pytest
from unittest.mock import AsyncMock, patch

from amon_claw.domain.entities.tenant import MessagingProvider, TenantMessagingConfig
from amon_claw.infrastructure.llm.tools.messaging_client import (
    EvolutionMessagingClient,
    TwilioMessagingClient,
    get_messaging_client,
)


@pytest.fixture
def twilio_config():
    return TenantMessagingConfig(
        provider=MessagingProvider.twilio,
        twilio_account_sid='AC123',
        twilio_auth_token='token',
        twilio_phone_number='+123456789',
    )


@pytest.fixture
def evolution_config():
    return TenantMessagingConfig(
        provider=MessagingProvider.evolution,
        evolution_api_url='https://evo.example.com',
        evolution_api_key='api-key',
        evolution_instance_name='instance1',
    )


def test_get_messaging_client_factory(twilio_config, evolution_config):
    # Test Twilio
    client = get_messaging_client(twilio_config)
    assert isinstance(client, TwilioMessagingClient)

    # Test Evolution
    client = get_messaging_client(evolution_config)
    assert isinstance(client, EvolutionMessagingClient)


@pytest.mark.asyncio
async def test_twilio_client_send_message(twilio_config):
    client = TwilioMessagingClient(twilio_config)

    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'sid': 'SM123'}
        mock_post.return_value = mock_response

        result = await client.send_message('+987654321', 'Hello')

        assert result == {'sid': 'SM123'}
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['data']['To'] == 'whatsapp:+987654321'
        assert kwargs['data']['From'] == 'whatsapp:+123456789'
        assert kwargs['data']['Body'] == 'Hello'


@pytest.mark.asyncio
async def test_evolution_client_send_message(evolution_config):
    client = EvolutionMessagingClient(evolution_config)

    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'status': 'success'}
        mock_post.return_value = mock_response

        result = await client.send_message('5511999999999', 'Hello')

        assert result == {'status': 'success'}
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['number'] == '5511999999999'
        assert kwargs['json']['text'] == 'Hello'
        assert kwargs['headers']['apikey'] == 'api-key'
