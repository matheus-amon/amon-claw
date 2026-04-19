# Spec - Integração de Interface de Chat (Twilio & Evolution API)

## 1. Visão Geral
Esta especificação define a implementação da camada de comunicação via WhatsApp do **Amon Claw**, utilizando webhooks do FastAPI para recebimento e clients abstratos para envio de mensagens.

## 2. Arquitetura

### 2.1. Endpoints de Webhook (Presentation)
Criar roteamento separado para cada provedor para facilitar a validação e o parsing:

- `POST /v1/webhooks/twilio/{tenant_id}`
  - Content-Type: `application/x-www-form-urlencoded`
  - Campos: `From`, `Body`, `MessageSid`
  - Segurança: Validar `X-Twilio-Signature` (opcional v1, recomendado v2)
- `POST /v1/webhooks/evolution/{tenant_id}`
  - Content-Type: `application/json`
  - Campos: `event` (filtrar `messages.upsert`), `data.key.fromMe` (filtrar `false`), `data.message` (extrair texto)
  - Segurança: Validar `apikey` no header (configurável por tenant)

### 2.2. Camada de Infraestrutura (Messaging Clients)
Utilizar o padrão Strategy com uma classe base abstrata.

**BaseMessagingClient (ABC):**
- `async send_text(to: str, text: str, config: dict) -> bool`
- `async send_image(to: str, url: str, caption: str, config: dict) -> bool`

**Implementações:**
1. `TwilioMessagingClient`: Usa `httpx` para `POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`.
2. `EvolutionMessagingClient`: Usa `httpx` para `POST {base_url}/message/sendText/{instance}`.

### 2.3. Modelagem de Dados (Tenant Config)
O modelo de `Tenant` deve incluir configurações de mensageria:
```python
class MessagingProvider(str, Enum):
    TWILIO = "twilio"
    EVOLUTION = "evolution"

class TenantMessagingConfig(BaseModel):
    provider: MessagingProvider
    # Twilio fields
    twilio_account_sid: Optional[str]
    twilio_auth_token: Optional[str]
    twilio_phone_number: Optional[str]
    # Evolution fields
    evolution_base_url: Optional[str]
    evolution_instance: Optional[str]
    evolution_apikey: Optional[str]
```

## 3. Fluxo de Processamento
1. **Webhook Recebido:**
   - Extrai `tenant_id` da URL.
   - Extrai `sender_number` e `message_text`.
2. **Orquestração (Application):**
   - Busca `Tenant` no MongoDB.
   - Instancia o Grafo do LangGraph usando o `sender_number` como `thread_id`.
   - O Grafo processa e retorna uma resposta.
3. **Resposta:**
   - O Grafo (ou um Use Case de saída) utiliza o `MessagingFactory` para obter o client correto do Tenant e enviar a mensagem de volta.

## 4. Próximos Passos (Plano)
1. Atualizar entidade `Tenant` e seu Schema/Model para incluir `messaging_config`.
2. Implementar `BaseMessagingClient` e os clients concretos.
3. Criar os roteadores de webhook no FastAPI.
4. Integrar o recebimento com a chamada do `sdr_assistant` (LangGraph).
