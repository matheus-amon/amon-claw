from pydantic import BaseModel, SecretStr
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from amon_claw.core.settings import settings_singleton


class MathResult(BaseModel):
    result: float
    explication: str


settings = settings_singleton()


def model_factory(
    api_key: SecretStr = settings.llm.openrouter_api_key,
    model_id: str = settings.llm.openrouter_model_id,
) -> OpenRouterModel:
    provider = OpenRouterProvider(api_key=api_key.get_secret_value())
    return OpenRouterModel(model_id, provider=provider)


def agent_factory() -> Agent:
    model = model_factory()
    return Agent(model, output_type=MathResult)  # pyright: ignore[reportReturnType]
