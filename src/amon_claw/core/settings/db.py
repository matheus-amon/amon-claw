from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    # MongoDB URI directly from MONGO_URI env var
    uri: str = Field(default='mongodb://localhost:27017/amon_claw', alias='MONGO_URI')
    db_name: str = Field(default='amon_claw', alias='MONGO_DB_NAME') # Assuming MONGO_DB_NAME env var as well

    # Redis settings
    redis_host: str = Field(default='localhost', alias='REDIS_HOST')
    redis_port: int = Field(default=6379, alias='REDIS_PORT')
