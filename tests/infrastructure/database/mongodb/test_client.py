# tests/infrastructure/database/mongodb/test_client.py

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from amon_claw.infrastructure.database.mongodb.client import get_mongo_client, get_mongo_db
from amon_claw.application.use_cases.appointment_persistence import save_appointment_to_db
from amon_claw.core.config import settings_singleton
import asyncio # Necessário para o `asyncio.run` em exemplos e para `pytest-asyncio`

# Fixture para garantir um cliente MongoDB assíncrono para cada teste
@pytest.fixture(name="mongo_client", scope="function")
async def mongo_client_fixture():
    # Assegura que o cliente MongoDB singleton seja redefinido para cada teste
    settings = settings_singleton()
    client = AsyncIOMotorClient(settings.db.uri)
    # Limpa o banco de dados de teste antes de cada teste
    await client[settings.db.db_name].command("dropDatabase")
    yield client
    # Limpa o banco de dados de teste depois de cada teste
    await client[settings.db.db_name].command("dropDatabase")
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
    assert db.name == settings_singleton().db.db_name
    # Verifica se é uma instância de um banco de dados Motor
    assert hasattr(db, 'command')

@pytest.mark.asyncio
async def test_save_appointment_to_db(mongo_client: AsyncIOMotorClient): # Injetar o fixture
    """Testa a funcionalidade de salvar agendamentos no MongoDB."""
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
    # Convertendo o inserted_id para ObjectId, se necessário, para a busca
    from bson.objectid import ObjectId
    inserted_doc = await appointments_collection.find_one({"_id": ObjectId(result["inserted_id"])})
    assert inserted_doc is not None
    assert inserted_doc["service"] == "Manicure"
    assert "created_at" in inserted_doc

    # Limpa o documento inserido após o teste (já coberto pelo fixture, mas boa prática)
    await appointments_collection.delete_one({"_id": ObjectId(result["inserted_id"])})
