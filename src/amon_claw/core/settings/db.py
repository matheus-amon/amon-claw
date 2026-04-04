from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    url: str = Field(default='sqlite:///./real_estate.db')
