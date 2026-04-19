from contextlib import asynccontextmanager

from fastapi import FastAPI

from amon_claw.core.config import settings_singleton
from amon_claw.infrastructure.database.mongodb.client import init_db

settings = settings_singleton()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    yield


def app_factory() -> FastAPI:
    app = FastAPI(
        debug=settings.api.debug,
        title='AmonClaw',
        version=settings.api.version,
        lifespan=lifespan,
    )

    @app.get('/health')
    def health_check():
        return {'status': 'ok', 'version': settings.api.version}

    return app


app = app_factory()
