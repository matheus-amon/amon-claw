import asyncio

import pytest
from beanie import init_beanie

# Patch mongomock_motor to handle authorizedCollections argument
from mongomock_motor import AsyncMongoMockClient, AsyncMongoMockDatabase

from amon_claw.infrastructure.database.mongodb.models import __all_models__

_original_list_collection_names = AsyncMongoMockDatabase.list_collection_names

async def _patched_list_collection_names(self, *args, **kwargs):
    # Remove all unknown kwargs, mongomock only supports session and filter
    supported_kwargs = {'filter', 'session'}
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in supported_kwargs}
    return await _original_list_collection_names(self, *args, **filtered_kwargs)

AsyncMongoMockDatabase.list_collection_names = _patched_list_collection_names

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def db_init():
    """Initialize Beanie with a mocked MongoDB client."""
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client.get_database("test_db"),
        document_models=__all_models__
    )
    yield
