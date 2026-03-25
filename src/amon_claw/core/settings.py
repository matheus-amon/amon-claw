from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    url: str = Field(default='sqlite:///./real_estate.db')


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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        str_to_lower=True,
        extra='allow',
    )

    environment: Literal['prod', 'dev'] = Field(default='dev')
    llm: LLMConfig = Field(default_factory=LLMConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)


@lru_cache(maxsize=1)
def settings_singleton() -> Settings:
    return Settings()
