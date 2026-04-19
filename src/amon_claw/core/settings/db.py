from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    uri: str = Field(default='mongodb://localhost:27017/amon_claw')
    db_name: str = Field(default='amon_claw')
