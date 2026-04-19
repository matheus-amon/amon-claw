from abc import ABC, abstractmethod
from typing import Any

import httpx

from amon_claw.domain.entities.tenant import MessagingProvider, TenantMessagingConfig


class BaseMessagingClient(ABC):
    @abstractmethod
    async def send_message(self, to: str, content: str) -> dict[str, Any]:
        """Envia uma mensagem para o destinatário."""
        pass


class TwilioMessagingClient(BaseMessagingClient):
    def __init__(self, config: TenantMessagingConfig):
        self.config = config
        self.auth = (config.twilio_account_sid, config.twilio_auth_token)
        self.base_url = (
            f'https://api.twilio.com/2010-04-01/Accounts/{config.twilio_account_sid}/Messages.json'
        )

    async def send_message(self, to: str, content: str) -> dict[str, Any]:
        # Formata os números no padrão whatsapp:+123456789
        from_number = self.config.twilio_phone_number
        if not from_number.startswith('whatsapp:'):
            from_number = f'whatsapp:{from_number}'

        to_number = to
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        async with httpx.AsyncClient() as client:
            data = {
                'From': from_number,
                'To': to_number,
                'Body': content,
            }
            response = await client.post(self.base_url, data=data, auth=self.auth)
            response.raise_for_status()
            return response.json()


class EvolutionMessagingClient(BaseMessagingClient):
    def __init__(self, config: TenantMessagingConfig):
        self.config = config
        self.base_url = (
            f'{config.evolution_api_url}/message/sendText/{config.evolution_instance_name}'
        )
        self.headers = {'apikey': config.evolution_api_key or ''}

    async def send_message(self, to: str, content: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {
                'number': to,
                'text': content,
            }
            response = await client.post(
                self.base_url, json=payload, headers=self.headers
            )
            response.raise_for_status()
            return response.json()


def get_messaging_client(config: TenantMessagingConfig) -> BaseMessagingClient:
    if config.provider == MessagingProvider.twilio:
        return TwilioMessagingClient(config)
    elif config.provider == MessagingProvider.evolution:
        return EvolutionMessagingClient(config)
    else:
        raise ValueError(f'Provedor de mensagens desconhecido: {config.provider}')
