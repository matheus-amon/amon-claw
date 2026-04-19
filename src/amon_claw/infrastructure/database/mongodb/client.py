# src/amon_claw/infrastructure/database/mongodb/client.py

from motor.motor_asyncio import AsyncIOMotorClient
from amon_claw.core.config import settings_singleton
from loguru import logger

_mongo_client: AsyncIOMotorClient | None = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Retorna uma instância singleton do cliente MongoDB assíncrono."""
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = AsyncIOMotorClient(settings_singleton().db.uri)
            # A conexão é estabelecida, mas para ter certeza que está ativa
            # podemos tentar uma operação, ou fazer o ping no exemplo de uso
            logger.info(f"Conectado ao MongoDB em {settings_singleton().db.uri}")
        except Exception as e:
            logger.error(f"Falha ao conectar ao MongoDB: {e}")
            raise
    return _mongo_client

def get_mongo_db():
    """Retorna a instância do banco de dados MongoDB."""
    client = get_mongo_client()
    return client[settings_singleton().db.db_name]

# Exemplo de uso (opcional, pode ser removido ou movido para testes)
if __name__ == "__main__":
    import asyncio
    async def test_connection():
        client = get_mongo_client()
        db = get_mongo_db()
        try:
            # Tentar uma operação real para verificar a conexão
            await client.admin.command('ping')
            logger.info("MongoDB ping bem-sucedido!")
            logger.info(f"Conectado ao banco de dados: {db.name}")
        except Exception as e:
            logger.error(f"Falha ao pingar MongoDB: {e}")
        finally:
            # Não fechar o cliente singleton aqui, pois pode ser usado por outras partes da aplicação
            # client.close() # Comentar ou remover em produção se o cliente for singleton

    asyncio.run(test_connection())
