from fastapi import FastAPI, Response
from amon_claw.core.config import settings_singleton

settings = settings_singleton()

def app_factory() -> FastAPI:
    app = FastAPI(
        debug=settings.api.debug,
        title='AmonClaw',
        version=settings.api.version,
    )

    @app.get("/health")
    def health_check():
        return {"status": "ok", "version": settings.api.version}

    return app

app = app_factory()
