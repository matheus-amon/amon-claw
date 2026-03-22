from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    url: str = Field(default='sqlite:///./real_estate.db')


class LLMConfig(BaseModel):
    api_key: SecretStr = Field(default=SecretStr(''))
    model_id: str = Field(default='nvidia/nemotron-3-super-120b-a12b:free')

    @field_validator('api_key')
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
        env_nested_delimiter='__',
    )

    environment: Literal['prod', 'dev'] = Field(default='dev')
    llm: LLMConfig = Field(default_factory=LLMConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
