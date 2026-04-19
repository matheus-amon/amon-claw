from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from amon_claw.core.config import settings_singleton
from amon_claw.infrastructure.database.mongodb.models import __all_models__


async def init_db():
    settings = settings_singleton()
    client = AsyncIOMotorClient(settings.db.uri)
    await init_beanie(
        database=client[settings.db.db_name], document_models=__all_models__
    )
