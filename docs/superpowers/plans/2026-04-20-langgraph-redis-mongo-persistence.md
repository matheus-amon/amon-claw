# LangGraph Redis Checkpointer and MongoDB Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement LangGraph com Redis como o checkpointer principal para gerenciamento de estado de alta performance, e integrar MongoDB para persistência de longo prazo de dados selecionados da aplicação.

**Architecture:** O LangGraph utilizará `RedisSaver` para o gerenciamento de seu estado interno, aproveitando a velocidade do Redis para o contexto de interação em tempo real. Dados específicos da aplicação, como agendamentos confirmados ou perfis de usuário, serão persistidos no MongoDB via ações explícitas (ferramentas) do agente dentro do fluxo do LangGraph, garantindo durabilidade e armazenamento de longo prazo para informações críticas.

**Tech Stack:** Python, LangGraph, Redis, MongoDB, `uv` (para gerenciamento de dependências), `pymongo`, `langgraph-checkpoint-redis`.

---

## File Structure

- Create: `src/amon_claw/infrastructure/database/redis/client.py`
  - Responsibility: Inicializar e prover a instância do cliente Redis e `RedisSaver`.
- Create: `src/amon_claw/infrastructure/database/mongodb/client.py`
  - Responsibility: Inicializar e prover a instância do cliente MongoDB e conexão com o banco de dados.
- Modify: `pyproject.toml`
  - Responsibility: Adicionar as dependências `langgraph-checkpoint-redis` e `pymongo`.
- Modify: `compose.yml`
  - Responsibility: Garantir que os serviços Redis e MongoDB estejam definidos e configurados corretamente.
- Modify: `src/amon_claw/core/config.py`
  - Responsibility: Definir as configurações de conexão para Redis e MongoDB.
- Modify: `src/amon_claw/main.py`
  - Responsibility: Integrar o `RedisSaver` com a aplicação LangGraph e fornecer mecanismos para interação com o MongoDB.
- Create: `src/amon_claw/application/use_cases/appointment_persistence.py`
  - Responsibility: Conter a lógica para salvar agendamentos ou outros dados específicos no MongoDB.
- Create: `tests/infrastructure/database/redis/test_client.py`
  - Responsibility: Testar a inicialização do cliente Redis e do `RedisSaver`.
- Create: `tests/infrastructure/database/mongodb/test_client.py`
  - Responsibility: Testar a inicialização do cliente MongoDB e a funcionalidade de persistência.

---

### Task 1: Atualizar `pyproject.toml` com novas dependências

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Adicionar as dependências `langgraph-checkpoint-redis` e `pymongo`**

```toml
# pyproject.toml

[project.dependencies]
python = ">=3.11,<3.13"
langchain = "^0.1.13"
langgraph = "^0.0.30"
pydantic = "^2.6.4"
python-dotenv = "^1.0.1"
uvicorn = "^0.28.0"
fastapi = "^0.110.0"
mkdocs = "^1.5.3"
mkdocs-material = "^9.5.15"
mkdocstrings = { extras = ["python"], version = "^0.24.0" }
loguru = "^0.7.2"
beanie = "^1.24.0"
motor = "^3.3.2"
langgraph-checkpoint-redis = "^0.0.1" # Adicionar esta linha
pymongo = "^4.6.2" # Adicionar esta linha

[tool.uv.sources]
# ... (restante do arquivo)
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "feat: Adiciona dependências para Redis Checkpointer e MongoDB"
```

### Task 2: Atualizar `compose.yml` para os serviços Redis e MongoDB

**Files:**
- Modify: `compose.yml`

- [ ] **Step 1: Adicionar/Verificar os serviços Redis e MongoDB**

```yaml
# compose.yml

services:
  amon_claw_app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      # Exemplo de variáveis de ambiente, ajuste conforme necessário
      REDIS_HOST: redis
      REDIS_PORT: 6379
      MONGO_URI: mongodb://mongo:27017/amon_claw_db
    depends_on:
      - redis
      - mongo

  redis:
    image: redis/redis-stack:latest # Usar redis-stack para módulos RedisJSON e RediSearch
    ports:
      - "6379:6379"
      - "8001:8001" # Porta para RedisInsight (opcional)
    volumes:
      - redis_data:/data # Volume persistente para dados do Redis

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db # Volume persistente para dados do MongoDB
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USERNAME} # Se usar autenticação
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD} # Se usar autenticação

volumes:
  redis_data:
  mongo_data:
```

- [ ] **Step 2: Commit**

```bash
git add compose.yml
git commit -m "infra: Adiciona e configura serviços Redis e MongoDB no compose.yml"
```

### Task 3: Adicionar configurações Redis e MongoDB a `amon_claw/core/config.py`

**Files:**
- Modify: `src/amon_claw/core/config.py`

- [ ] **Step 1: Adicionar variáveis de ambiente para Redis e MongoDB**

```python
# src/amon_claw/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ... (outras configurações existentes)

    # Configurações do Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Configurações do MongoDB
    MONGO_URI: str = "mongodb://localhost:27017/amon_claw_db"
    MONGO_DB_NAME: str = "amon_claw_db" # Pode ser inferido da URI, mas é bom ter explícito

settings = Settings()
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/core/config.py
git commit -m "feat: Adiciona configurações para Redis e MongoDB"
```

### Task 4: Implementar Cliente Redis e `RedisSaver` em `amon_claw/infrastructure/database/redis/client.py`

**Files:**
- Create: `src/amon_claw/infrastructure/database/redis/client.py`

- [ ] **Step 1: Criar o arquivo `client.py` com o cliente Redis e `RedisSaver`**

```python
# src/amon_claw/infrastructure/database/redis/client.py

from redis import Redis
from langgraph.checkpoint.redis import RedisSaver
from amon_claw.core.config import settings
from loguru import logger

_redis_client: Redis | None = None
_redis_saver: RedisSaver | None = None

def get_redis_client() -> Redis:
    """Retorna uma instância singleton do cliente Redis."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True # Decodifica respostas para string por padrão
            )
            _redis_client.ping() # Testa a conexão
            logger.info(f"Conectado ao Redis em {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"Falha ao conectar ao Redis: {e}")
            raise
    return _redis_client

def get_redis_saver() -> RedisSaver:
    """Retorna uma instância singleton do RedisSaver para LangGraph."""
    global _redis_saver
    if _redis_saver is None:
        redis_client = get_redis_client()
        _redis_saver = RedisSaver(redis_client=redis_client)
        logger.info("RedisSaver para LangGraph inicializado.")
    return _redis_saver

# Exemplo de uso (opcional, pode ser removido ou movido para testes)
if __name__ == "__main__":
    client = get_redis_client()
    saver = get_redis_saver()
    print("Redis client e saver obtidos com sucesso!")
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/infrastructure/database/redis/client.py
git commit -m "feat: Implementa cliente Redis e RedisSaver para LangGraph"
```

### Task 5: Implementar Cliente MongoDB em `amon_claw/infrastructure/database/mongodb/client.py`

**Files:**
- Create: `src/amon_claw/infrastructure/database/mongodb/client.py`

- [ ] **Step 1: Criar o arquivo `client.py` com o cliente MongoDB**

```python
# src/amon_claw/infrastructure/database/mongodb/client.py

from motor.motor_asyncio import AsyncIOMotorClient
from amon_claw.core.config import settings
from loguru import logger

_mongo_client: AsyncIOMotorClient | None = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Retorna uma instância singleton do cliente MongoDB assíncrono."""
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
            # Testar a conexão (ex: listar nomes de dbs)
            # await _mongo_client.list_database_names() # Não é possível em sync context
            logger.info(f"Conectado ao MongoDB em {settings.MONGO_URI}")
        except Exception as e:
            logger.error(f"Falha ao conectar ao MongoDB: {e}")
            raise
    return _mongo_client

def get_mongo_db():
    """Retorna a instância do banco de dados MongoDB."""
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]

# Exemplo de uso (opcional, pode ser removido ou movido para testes)
if __name__ == "__main__":
    import asyncio
    async def test_connection():
        client = get_mongo_client()
        db = get_mongo_db()
        try:
            await client.admin.command('ping')
            logger.info("MongoDB ping bem-sucedido!")
            logger.info(f"Conectado ao banco de dados: {db.name}")
        except Exception as e:
            logger.error(f"Falha ao pingar MongoDB: {e}")
        finally:
            client.close()

    asyncio.run(test_connection())

```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/infrastructure/database/mongodb/client.py
git commit -m "feat: Implementa cliente MongoDB assíncrono"
```

### Task 6: Integrar `RedisSaver` na aplicação LangGraph em `amon_claw/main.py`

**Files:**
- Modify: `src/amon_claw/main.py`

- [ ] **Step 1: Importar e usar `get_redis_saver` ao compilar o grafo**

```python
# src/amon_claw/main.py

# ... (outros imports)
from langgraph.graph import StateGraph, END
from amon_claw.infrastructure.database.redis.client import get_redis_saver
from loguru import logger
from typing import TypedDict, Annotated
import operator
import asyncio # Para rodar o exemplo async

class AgentState(TypedDict):
    """Representa o estado do agente."""
    messages: Annotated[list, operator.add]
    # Outros campos de estado aqui

def create_langgraph_app():
    # Exemplo de grafo simples, substitua pela sua lógica
    workflow = StateGraph(AgentState)

    def agent_node(state):
        logger.info(f"Executando agent_node com estado: {state}")
        # Lógica do seu agente aqui
        return {"messages": ["Agent response!"]}

    workflow.add_node("agent", agent_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END) # Ou para outro nó

    checkpointer = get_redis_saver() # Obter o RedisSaver
    app = workflow.compile(checkpointer=checkpointer)
    logger.info("LangGraph app compilado com RedisSaver.")
    return app

# Exemplo de uso
if __name__ == "__main__":
    from pprint import pprint
    async def run_app_example():
        app = create_langgraph_app()

        # Usar um thread_id configurável para a persistência
        # Cada interação com um thread_id diferente cria/carrega um checkpoint diferente
        config = {"configurable": {"thread_id": "test_session_123"}}

        # Invocação inicial
        inputs = {"messages": ["Olá, como posso ajudar?"]}
        response = await app.ainvoke(inputs, config=config)
        logger.info("Primeira invocação:")
        pprint(response)

        # Invocação subsequente com o mesmo thread_id deve retomar o estado
        inputs_2 = {"messages": ["Qual é o status do meu pedido?"]}
        response_2 = await app.ainvoke(inputs_2, config=config)
        logger.info("Segunda invocação (mesmo thread_id):")
        pprint(response_2)

        # Note que o RedisSaver salva o estado em 'messages', então a segunda
        # invocação terá as mensagens da primeira + as da segunda.
    asyncio.run(run_app_example())
```

- [ ] **Step 2: Commit**

```bash
git add src/amon_claw/main.py
git commit -m "feat: Integra RedisSaver no LangGraph em main.py"
```

### Task 7: Criar uma funcionalidade básica de persistência para MongoDB

Essa tarefa visa criar uma "ferramenta" (função) que o LangGraph possa chamar para salvar dados específicos no MongoDB. Isso simula a ação do agente de "persistir o agendamento concluído".

**Files:**
- Create: `src/amon_claw/application/use_cases/appointment_persistence.py`
- Modify: `src/amon_claw/main.py` (para incluir e usar essa ferramenta)

- [ ] **Step 1: Criar o arquivo `appointment_persistence.py`**

```python
# src/amon_claw/application/use_cases/appointment_persistence.py

from amon_claw.infrastructure.database.mongodb.client import get_mongo_db
from loguru import logger
from typing import Any
import datetime

async def save_appointment_to_db(appointment_data: dict[str, Any]) -> dict[str, Any]:
    """
    Salva dados de um agendamento concluído ou importante no MongoDB.
    Esta função seria chamada por uma 'ferramenta' do LangGraph.
    """
    db = get_mongo_db()
    appointments_collection = db.appointments # Nome da coleção

    # Adiciona um timestamp para registro
    appointment_data["created_at"] = datetime.datetime.now(datetime.timezone.utc)

    try:
        result = await appointments_collection.insert_one(appointment_data)
        logger.info(f"Agendamento salvo no MongoDB com ID: {result.inserted_id}")
        return {"status": "success", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Erro ao salvar agendamento no MongoDB: {e}")
        return {"status": "error", "message": str(e)}

# Exemplo de como um tool poderia ser definido (não é a implementação real da ferramenta LangGraph aqui)
# from langchain_core.tools import tool
# @tool
# async def persist_final_appointment_details(data: dict[str, Any]) -> str:
#     """Persiste os detalhes finais de um agendamento no banco de dados."""
#     response = await save_appointment_to_db(data)
#     return str(response)
```

- [ ] **Step 2: Modificar `main.py` para integrar a funcionalidade de persistência (exemplo com uma "tool" fictícia)**

```python
# src/amon_claw/main.py

# ... (outros imports)
from langgraph.graph import StateGraph, END
from amon_claw.infrastructure.database.redis.client import get_redis_saver
from amon_claw.application.use_cases.appointment_persistence import save_appointment_to_db # Novo import
from loguru import logger
from typing import TypedDict, Annotated
import operator
import asyncio # Para rodar o exemplo async

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    appointment_details: dict # Novo campo para detalhes do agendamento

# Define um nó que simula a decisão de salvar no MongoDB
async def save_to_mongo_node(state: AgentState):
    logger.info(f"Executando save_to_mongo_node. Estado: {state}")
    if state.get("appointment_details"):
        # Chamar a função de persistência
        result = await save_appointment_to_db(state["appointment_details"])
        logger.info(f"Resultado da persistência no MongoDB: {result}")
        return {"messages": [f"Agendamento persistido. Status: {result.get('status')}"]}
    return {"messages": ["Nenhum detalhe de agendamento para persistir."]}

def create_langgraph_app():
    workflow = StateGraph(AgentState)

    def agent_node(state):
        logger.info(f"Executando agent_node com estado: {state}")
        # Simula o agente identificando um agendamento e adicionando detalhes ao estado
        current_messages = state.get("messages", [])
        if any("marcar corte" in msg for msg in current_messages):
            logger.info("Agente identificou intenção de marcar corte.")
            # Simula a extração de detalhes do agendamento, incluindo a "prioridade"
            appointment_details = {
                "service": "Corte de Cabelo",
                "date": "2026-04-25",
                "time": "10:00",
                "priority": True, # A informação temporária de prioridade
                "client_name": "Amon"
            }
            return {"messages": ["Ok, vamos marcar seu corte!"], "appointment_details": appointment_details}
        return {"messages": ["Agent response!"]}

    workflow.add_node("agent", agent_node)
    workflow.add_node("persist_appointment", save_to_mongo_node) # Adiciona o novo nó

    workflow.set_entry_point("agent")
    workflow.add_edge("agent", "persist_appointment") # Agente -> Persistir
    workflow.add_edge("persist_appointment", END) # Persistir -> Fim

    checkpointer = get_redis_saver()
    app = workflow.compile(checkpointer=checkpointer)
    logger.info("LangGraph app compilado com RedisSaver e persistência MongoDB.")
    return app

# Exemplo de uso
if __name__ == "__main__":
    from pprint import pprint
    async def run_app_example():
        app = create_langgraph_app()
        config = {"configurable": {"thread_id": "test_session_mongo"}}

        # Simula uma conversa onde um agendamento é marcado e persistido
        inputs = {"messages": ["Quero marcar um corte de cabelo com prioridade!"]}
        response = await app.ainvoke(inputs, config=config)
        logger.info("Primeira invocação (agendamento):")
        pprint(response)

        # Invocação subsequente com o mesmo thread_id
        inputs_2 = {"messages": ["Obrigado!"]}
        response_2 = await app.ainvoke(inputs_2, config=config)
        logger.info("Segunda invocação (mesmo thread_id):")
        pprint(response_2)

    asyncio.run(run_app_example())
```

- [ ] **Step 3: Commit**

```bash
git add src/amon_claw/application/use_cases/appointment_persistence.py src/amon_claw/main.py
git commit -m "feat: Adiciona funcionalidade de persistência MongoDB e integra ao LangGraph"
```

### Task 8: Adicionar testes para o Cliente Redis e `RedisSaver`

**Files:**
- Create: `tests/infrastructure/database/redis/test_client.py`

- [ ] **Step 1: Criar o arquivo `test_client.py` para o Redis**

```python
# tests/infrastructure/database/redis/test_client.py

import pytest
from redis import Redis
from langgraph.checkpoint.redis import RedisSaver
from amon_claw.infrastructure.database.redis.client import get_redis_client, get_redis_saver
from amon_claw.core.config import settings

# Usar um fixture para garantir um cliente Redis limpo para cada teste
@pytest.fixture(name="redis_client", scope="function")
def redis_client_fixture():
    # Assegura que o cliente Redis singleton seja redefinido para cada teste
    # para evitar interferência entre testes.
    # Em um ambiente de teste real, você pode querer um Redis de teste separado
    # ou mockar a conexão. Aqui, estamos usando a conexão real definida em settings.
    client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    client.flushdb() # Limpa o banco de dados Redis para cada teste
    yield client
    client.flushdb()
    client.close()

def test_get_redis_client(redis_client: Redis):
    """Testa se o cliente Redis é obtido e está funcionando."""
    assert isinstance(redis_client, Redis)
    assert redis_client.ping()

def test_get_redis_saver(redis_client: Redis):
    """Testa se o RedisSaver é obtido e usa o cliente Redis correto."""
    saver = get_redis_saver()
    assert isinstance(saver, RedisSaver)
    # Verifica se o cliente interno do saver é o que esperamos
    assert saver.red.connection_pool.connection_kwargs['host'] == settings.REDIS_HOST
    assert saver.red.connection_pool.connection_kwargs['port'] == settings.REDIS_PORT

def test_redis_saver_checkpoint_functionality(redis_client: Redis):
    """Testa a funcionalidade básica de checkpoint do RedisSaver."""
    saver = get_redis_saver()
    thread_id = "test_thread_123"
    config = {"configurable": {"thread_id": thread_id}}

    # Salva um estado inicial
    initial_state = {"messages": [{"role": "user", "content": "Hello!"}], "steps": 1}
    saver.put(config, initial_state)

    # Verifica se o estado foi salvo
    retrieved_state = saver.get(config)
    assert retrieved_state is not None
    assert retrieved_state["checkpoint"]["payload"] == initial_state

    # Salva um novo estado (simulando uma atualização)
    updated_state = {"messages": [{"role": "assistant", "content": "Hi there!"}], "steps": 2}
    saver.put(config, updated_state)

    # Verifica se o estado atualizado foi salvo
    retrieved_updated_state = saver.get(config)
    assert retrieved_updated_state is not None
    assert retrieved_updated_state["checkpoint"]["payload"] == updated_state

    # Verifica se a chave existe no Redis
    assert redis_client.exists(f"langgraph_checkpoint_{thread_id}")

    # Testar se um thread_id inexistente retorna None
    non_existent_config = {"configurable": {"thread_id": "non_existent"}}
    assert saver.get(non_existent_config) is None
```

- [ ] **Step 2: Rodar os testes para verificar o comportamento**

Run: `pytest tests/infrastructure/database/redis/test_client.py`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/infrastructure/database/redis/test_client.py
git commit -m "test: Adiciona testes para cliente Redis e RedisSaver"
```

### Task 9: Adicionar testes para o Cliente MongoDB

**Files:**
- Create: `tests/infrastructure/database/mongodb/test_client.py`

- [ ] **Step 1: Criar o arquivo `test_client.py` para o MongoDB**

```python
# tests/infrastructure/database/mongodb/test_client.py

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from amon_claw.infrastructure.database.mongodb.client import get_mongo_client, get_mongo_db
from amon_claw.core.config import settings
import asyncio

# Fixture para garantir um cliente MongoDB assíncrono para cada teste
@pytest.fixture(name="mongo_client", scope="function")
async def mongo_client_fixture():
    # Assegura que o cliente MongoDB singleton seja redefinido para cada teste
    client = AsyncIOMotorClient(settings.MONGO_URI)
    # Limpa o banco de dados de teste antes de cada teste
    await client[settings.MONGO_DB_NAME].command("dropDatabase")
    yield client
    # Limpa o banco de dados de teste depois de cada teste
    await client[settings.MONGO_DB_NAME].command("dropDatabase")
    client.close()

@pytest.mark.asyncio
async def test_get_mongo_client(mongo_client: AsyncIOMotorClient):
    """Testa se o cliente MongoDB assíncrono é obtido e está funcionando."""
    assert isinstance(mongo_client, AsyncIOMotorClient)
    # Tenta pingar o servidor para verificar a conexão
    result = await mongo_client.admin.command('ping')
    assert result['ok'] == 1.0

@pytest.mark.asyncio
async def test_get_mongo_db(mongo_client: AsyncIOMotorClient):
    """Testa se o banco de dados MongoDB é obtido corretamente."""
    db = get_mongo_db()
    assert db.name == settings.MONGO_DB_NAME
    # Verifica se é uma instância de um banco de dados Motor
    assert hasattr(db, 'command')

@pytest.mark.asyncio
async def test_save_appointment_to_db():
    """Testa a funcionalidade de salvar agendamentos no MongoDB."""
    from amon_claw.application.use_cases.appointment_persistence import save_appointment_to_db
    db = get_mongo_db()
    appointments_collection = db.appointments

    test_appointment = {
        "service": "Manicure",
        "date": "2026-05-01",
        "time": "14:00",
        "client_name": "Maria",
        "priority": False
    }

    result = await save_appointment_to_db(test_appointment)
    assert result["status"] == "success"
    assert "inserted_id" in result

    # Verifica se o documento foi realmente inserido
    inserted_doc = await appointments_collection.find_one({"_id": result["inserted_id"]})
    assert inserted_doc is not None
    assert inserted_doc["service"] == "Manicure"
    assert "created_at" in inserted_doc

    # Limpa o documento inserido após o teste
    await appointments_collection.delete_one({"_id": result["inserted_id"]})
```

- [ ] **Step 2: Rodar os testes para verificar o comportamento**

Run: `pytest tests/infrastructure/database/mongodb/test_client.py`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/infrastructure/database/mongodb/test_client.py
git commit -m "test: Adiciona testes para cliente MongoDB e funcionalidade de persistência"
```

---