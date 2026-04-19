from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_', # Keep this for MongoDB settings
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    uri: str = Field(default='mongodb://localhost:27017/amon_claw')
    db_name: str = Field(default='amon_claw')

    # Redis settings
    # Override env var names as they don't have the 'DB_' prefix
    redis_host: str = Field(default='localhost', alias='REDIS_HOST')
    redis_port: int = Field(default=6379, alias='REDIS_PORT')
