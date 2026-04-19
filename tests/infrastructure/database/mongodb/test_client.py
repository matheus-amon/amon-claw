import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from amon_claw.infrastructure.database.mongodb.client import get_mongo_client, get_mongo_db, _mongo_client # Import _mongo_client for reset
from amon_claw.application.use_cases.appointment_persistence import save_appointment_to_db
from amon_claw.core.config import settings_singleton
import asyncio
from bson.objectid import ObjectId
import pymongo # Import pymongo for exceptions
from urllib.parse import urlparse # Import urlparse

# Fixture para garantir um cliente MongoDB assíncrono para cada teste
@pytest.fixture(name="mongo_client", scope="function")
async def mongo_client_fixture():
    # Reset the global singleton client used by get_mongo_client/get_mongo_db for test isolation
    global _mongo_client
    _mongo_client = None

    settings = settings_singleton()
    print(f"DEBUG: MongoDB URI used in fixture: {settings.db.uri}") # Keep for debugging

    # Extract username and password from the URI for explicit authentication
    parsed_uri = urlparse(settings.db.uri)
    username = parsed_uri.username if parsed_uri.username else "admin" # Default to admin if not in URI
    password = parsed_uri.password if parsed_uri.password else "password" # Default to password if not in URI
    host = parsed_uri.hostname if parsed_uri.hostname else "localhost"
    port = parsed_uri.port if parsed_uri.port else 27017
    db_name_from_uri = parsed_uri.path.strip('/') if parsed_uri.path else settings.db.db_name

    # Create a new AsyncIOMotorClient for the fixture, explicitly authenticating
    client = AsyncIOMotorClient(
        host=host,
        port=port,
        username=username,
        password=password,
        authSource='admin', # Authenticate against the admin database
        uuidRepresentation='standard' # Recommended for MongoDB 4+
    )
    
    # Attempt to drop the database, handling potential authentication context
    try:
        # Ping the admin database to check connectivity and auth as superuser context
        await client.admin.command('ping')
        print("DEBUG: Ping successful with explicit authentication in fixture.")

        # Drop the specific database for the test
        # Use client.drop_database directly, as it handles authentication context
        await client.drop_database(db_name_from_uri) # Use db_name parsed from URI for consistency
        print(f"DEBUG: Successfully dropped database: {db_name_from_uri}")

    except pymongo.errors.OperationFailure as e:
        print(f"DEBUG: OperationFailure during setup (dropDatabase): {e}")
        raise
    except Exception as e:
        print(f"DEBUG: Other error during setup (dropDatabase): {e}")
        raise

    yield client # Yield the client for tests to use

    # Cleanup after test
    try:
        await client.drop_database(db_name_from_uri)
        print(f"DEBUG: Successfully dropped database during teardown: {db_name_from_uri}")
    except Exception as e:
        print(f"DEBUG: Error during teardown: {e}")
    client.close() # Close the client opened by the fixture

@pytest.mark.asyncio
async def test_get_mongo_client(mongo_client: AsyncIOMotorClient):
    """Testa se o cliente MongoDB assíncrono é obtido e está funcionando."""
    assert isinstance(mongo_client, AsyncIOMotorClient)
    result = await mongo_client.admin.command('ping')
    assert result['ok'] == 1.0

@pytest.mark.asyncio
async def test_get_mongo_db(mongo_client: AsyncIOMotorClient):
    """Testa se o banco de dados MongoDB é obtido corretamente."""
    db = get_mongo_db() # This will use the singleton client, which might be new or reused.
    assert db.name == settings_singleton().db.db_name
    assert hasattr(db, 'command')

@pytest.mark.asyncio
async def test_save_appointment_to_db(mongo_client: AsyncIOMotorClient):
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

    inserted_doc = await appointments_collection.find_one({"_id": ObjectId(result["inserted_id"])})
    assert inserted_doc is not None
    assert inserted_doc["service"] == "Manicure"
    assert "created_at" in inserted_doc

    await appointments_collection.delete_one({"_id": ObjectId(result["inserted_id"])})
