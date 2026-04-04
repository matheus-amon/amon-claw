from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='LLM_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    openrouter_api_key: SecretStr = Field(default=SecretStr(''))
    openrouter_model_id: str = Field(default='nvidia/nemotron-3-super-120b-a12b:free')

    @field_validator('openrouter_api_key')
    @classmethod
    def not_empty(cls, v: SecretStr) -> SecretStr:
        if not v.get_secret_value():
            raise ValueError('OPENROUTER_API_KEY is empty')
        return v
