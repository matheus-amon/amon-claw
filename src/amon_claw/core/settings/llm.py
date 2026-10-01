from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def configured_model_id(config: 'LLMConfig') -> str:
    """The OpenRouter model to use, honouring a pin when one is set.

    A pin is the operator saying "I know what I want", so it short-circuits the
    catalogue entirely — no network call, and no failure when OpenRouter is down.
    Empty means "resolve", because a hardcoded `:free` id is a bet on an id that
    eventually gets retired.
    """
    pinned = config.openrouter_model_id.strip()
    if pinned:
        return pinned

    from amon_claw.infrastructure.llm.models.resolve_free_model import resolve_free_model

    resolved = resolve_free_model()
    return f'openrouter/{resolved}'


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='LLM_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    openrouter_api_key: SecretStr = Field(default=SecretStr(''))

    # Empty means "resolve from the live free catalogue" (see
    # infrastructure/llm/models/free_models.py). Set it only to pin a specific
    # model; a pin whose id has been retired degrades to the best free model
    # rather than failing, so this is a preference, not a dependency.
    openrouter_model_id: str = Field(default='')

    @field_validator('openrouter_api_key')
    @classmethod
    def not_empty(cls, v: SecretStr) -> SecretStr:
        if not v.get_secret_value():
            raise ValueError('OPENROUTER_API_KEY is empty')
        return v
