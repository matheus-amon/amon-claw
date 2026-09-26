# src/amon_claw/infrastructure/database/mongodb/client.py

from urllib.parse import urlparse  # Import urlparse

from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from amon_claw.core.config import settings_singleton
from amon_claw.infrastructure.database.mongodb.models import __all_models__

_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Retorna uma instância singleton do cliente MongoDB assíncrono."""
    global _mongo_client
    if _mongo_client is None:
        try:
            uri = settings_singleton().db.uri
            logger.info(
                f'DEBUG: Attempting to connect to MongoDB with URI from settings: {uri}'
            )  # Debugging

            # Parse URI to extract credentials for explicit authentication
            parsed_uri = urlparse(uri)
            username = parsed_uri.username if parsed_uri.username else None
            password = parsed_uri.password if parsed_uri.password else None
            host = parsed_uri.hostname if parsed_uri.hostname else 'localhost'
            port = parsed_uri.port if parsed_uri.port else 27017
            auth_source = 'admin'  # Assuming authentication always against admin database

            _mongo_client = AsyncIOMotorClient(
                host=host,
                port=port,
                username=username,
                password=password,
                authSource=auth_source,
                uuidRepresentation='standard',  # Recommended for MongoDB 4+
            )

            # Removed: _mongo_client.admin.command('ping') as it might interfere with event loop management in tests.
            logger.info(
                f'Conectado ao MongoDB em {uri} com autenticação explícita (sem ping inicial).'
            )
        except Exception as e:
            logger.error(f'Falha ao conectar ao MongoDB: {e}')
            raise
    return _mongo_client


def get_mongo_db():
    """Retorna a instância do banco de dados MongoDB."""
    client = get_mongo_client()
    return client[settings_singleton().db.db_name]


async def init_db() -> None:
    """Inicializa o Beanie com o cliente e o banco já configurados.

    Deve ser chamada uma única vez, na inicialização da aplicação, antes de
    qualquer repositório ser utilizado.
    """
    client = get_mongo_client()
    db = get_mongo_db()
    await init_beanie(database=db, document_models=__all_models__)
    logger.info(f'Beanie inicializado no banco "{db.name}" com {len(__all_models__)} modelos.')


# Exemplo de uso (opcional, pode ser removido ou movido para testes)
if __name__ == '__main__':
    import asyncio

    async def test_connection():
        client = get_mongo_client()
        db = get_mongo_db()
        try:
            await client.admin.command(
                'ping'
            )  # Keep ping in example as it's a direct run
            logger.info('MongoDB ping bem-sucedido!')
            logger.info(f'Conectado ao banco de dados: {db.name}')
        except Exception as e:
            logger.error(f'Falha ao pingar MongoDB: {e}')
        finally:
            pass  # Adicionar pass para bloco finally vazio

    asyncio.run(test_connection())
