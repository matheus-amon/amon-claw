from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from amon_claw.core.settings.api import ApiConfig
from amon_claw.core.settings.db import DatabaseConfig
from amon_claw.core.settings.llm import LLMConfig


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
    api: ApiConfig = Field(default_factory=ApiConfig)


@lru_cache(maxsize=1)
def settings_singleton() -> Settings:
    return Settings()
