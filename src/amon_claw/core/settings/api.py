from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='API_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    debug: bool = Field(default=True)
    version: str = Field(default='0.0.1')
