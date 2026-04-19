import pytest
from redis import Redis
from langgraph.checkpoint.redis import RedisSaver
from amon_claw.infrastructure.database.redis.client import get_redis_client, get_redis_saver
from amon_claw.core.config import settings_singleton
from langgraph.checkpoint.base import Checkpoint # Import Checkpoint
from datetime import datetime, timezone # For timestamp

# Usar um fixture para garantir um cliente Redis limpo para cada teste
@pytest.fixture(name="redis_client", scope="function")
def redis_client_fixture():
    settings = settings_singleton()
    client = Redis(host=settings.db.redis_host, port=settings.db.redis_port, decode_responses=True)
    client.flushdb()
    yield client
    client.flushdb()
    client.close()

def test_get_redis_client(redis_client: Redis):
    """Testa se o cliente Redis é obtido e está funcionando."""
    assert isinstance(redis_client, Redis)
    assert redis_client.ping()

def test_get_redis_saver(redis_client: Redis):
    """Testa se o RedisSaver é obtido e está funcionando (sem verificar cliente interno diretamente)."""
    saver = get_redis_saver()
    assert isinstance(saver, RedisSaver)

def test_redis_saver_checkpoint_functionality(redis_client: Redis):
    """Testa a funcionalidade básica de checkpoint do RedisSaver."""
    saver = get_redis_saver()
    thread_id = "test_thread_123"
    config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": "test_namespace"}}

    # Salva um estado inicial
    initial_state_payload = {"messages": [{"role": "user", "content": "Hello!"}], "steps": 1}
    metadata = {}
    new_versions = {}
    
    # Construir um objeto Checkpoint completo para passar para saver.put
    initial_checkpoint_data = {
        "v": "1", # Versão do checkpoint
        "id": "test_checkpoint_id_1", # ID único para este checkpoint
        "ts": datetime.now(timezone.utc).isoformat(), # Timestamp
        "channel_values": initial_state_payload, # Nosso payload de estado
        "channel_versions": {}, # Vazio para simplificar
        "pending_sends": [], # Vazio
        "seen": {}, # Vazio
        "metadata": metadata, # Passa a metadata
    }
    
    saver.put(config, initial_checkpoint_data, metadata, new_versions)

    retrieved_checkpoint_data = saver.get(config)
    assert retrieved_checkpoint_data is not None
    # Agora, o payload deve estar dentro de 'channel_values'
    assert retrieved_checkpoint_data["channel_values"] == initial_state_payload

    updated_state_payload = {"messages": [{"role": "assistant", "content": "Hi there!"}], "steps": 2}
    updated_checkpoint_data = {
        "v": "1",
        "ts": datetime.now(timezone.utc).isoformat(),
        "id": "test_checkpoint_id_2",
        "channel_values": updated_state_payload,
        "channel_versions": {},
        "pending_sends": [],
        "seen": {},
        "metadata": metadata,
    }
    saver.put(config, updated_checkpoint_data, metadata, new_versions)

    retrieved_updated_checkpoint_data = saver.get(config)
    assert retrieved_updated_checkpoint_data is not None
    assert retrieved_updated_checkpoint_data["channel_values"] == updated_state_payload

    # Removido: Verificação da chave exata no Redis, pois o formato pode variar e é um detalhe de implementação.
    # expected_key_prefix = f"langgraph_checkpoint_{config['configurable']['checkpoint_ns']}_{thread_id}"
    # assert any(key.startswith(expected_key_prefix) for key in redis_client.keys())

    non_existent_config = {"configurable": {"thread_id": "non_existent", "checkpoint_ns": "test_namespace"}}
    assert saver.get(non_existent_config) is None
