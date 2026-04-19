# src/amon_claw/infrastructure/database/redis/client.py

from redis import Redis
from langgraph.checkpoint.redis import RedisSaver
from amon_claw.core.config import settings_singleton # Usar settings_singleton
from loguru import logger

_redis_client: Redis | None = None
_redis_saver: RedisSaver | None = None

def get_redis_client() -> Redis:
    """Retorna uma instância singleton do cliente Redis."""
    global _redis_client
    if _redis_client is None:
        try:
            # Acessar configurações Redis através de settings_singleton().db
            _redis_client = Redis(
                host=settings_singleton().db.redis_host,
                port=settings_singleton().db.redis_port,
                decode_responses=True # Decodifica respostas para string por padrão
            )
            _redis_client.ping() # Testa a conexão
            logger.info(f"Conectado ao Redis em {settings_singleton().db.redis_host}:{settings_singleton().db.redis_port}")
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
