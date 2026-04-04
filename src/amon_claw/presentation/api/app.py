from fastapi import FastAPI

from amon_claw.core.config import settings_singleton

settings = settings_singleton()


def app_factory() -> FastAPI:
    app = FastAPI(
        debug=settings.api.debug,
        title='AmonClaw',
        version=settings.api.version,
    )
    return app
