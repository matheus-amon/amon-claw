# Design Spec: Admin Flow (WhatsApp First)

## Contexto
O Amon-Claw precisa permitir que os donos dos negócios (Tenants) configurem horários de funcionamento e catálogo de produtos/serviços diretamente pelo WhatsApp, sem a necessidade de uma interface web complexa inicial.

## Objetivos
- Autenticação simplificada via comando `/admin <hash>`.
- Roteamento dinâmico entre o fluxo de SDR (cliente) e Admin (dono).
- Gestão de horários de funcionamento e serviços via ferramentas de IA (Pydantic AI).

## Arquitetura de Roteamento (LangGraph)

### 1. Router Node (Ponto de Entrada)
Um nó inicial no `SDRGraph` que analisa a mensagem de entrada:
- **Padrão:** `^/admin\s+([a-zA-Z0-9]+)$`
- **Ação:** Se o padrão bater, extrai o `<hash>`, busca o `Tenant` associado no MongoDB e, se válido, redireciona o estado da conversa para o `AdminGraph`. Caso contrário, retorna erro de permissão.
- **Duração da Sessão Admin:** O estado de "modo admin" deve ter um TTL ou um comando de saída (ex: `/exit`) para voltar ao fluxo de SDR.

### 2. Admin Graph
Um sub-grafo especializado que utiliza o `AdminAgent` (Pydantic AI).
- **Prompt System:** "Você é o assistente administrativo do Amon-Claw. Seu objetivo é ajudar o dono do negócio a configurar horários, serviços e produtos. Seja direto e execute as ferramentas conforme solicitado."

## Ferramentas (Admin Tools)

### `update_business_hours`
- **Input:** `day_of_week` (enum), `open_time` (string), `close_time` (string), `is_closed` (bool).
- **Ação:** Atualiza o campo `business_hours` na entidade `Tenant` no MongoDB.

### `upsert_product_service`
- **Input:** `name` (string), `price` (float), `duration_minutes` (int), `description` (string).
- **Ação:** Adiciona ou atualiza um item na lista de `services` do `Tenant`. Se o nome já existir, atualiza os valores.

### `list_catalog`
- **Input:** Nenhum.
- **Ação:** Retorna a lista formatada de todos os serviços e horários atuais para conferência do dono.

## Modelo de Dados (Extensões)

No schema do `Tenant` (via Beanie):
```python
class BusinessHour(BaseModel):
    day: str  # monday, tuesday...
    open: str # "08:00"
    close: str # "18:00"
    is_closed: bool = False

class Service(BaseModel):
    name: str
    price: float
    duration: int # em minutos
    description: Optional[str]

# Tenant já possui: name, slug, phone, admin_hash...
```

## Segurança
- O `admin_hash` é um segredo único por Tenant gerado no setup inicial.
- A validação ocorre em cada transição para o `AdminGraph`.
- Mensagens que não começam com `/admin` ou não estão em "modo admin" ativo são tratadas como mensagens de cliente pelo `SDRGraph`.

## Próximos Passos
1. Implementar o nó de roteamento no `sdr_graph.py`.
2. Criar o sub-grafo `AdminGraph`.
3. Definir as ferramentas `AdminTools` usando Pydantic AI.
4. Testar a persistência no MongoDB via Beanie.
