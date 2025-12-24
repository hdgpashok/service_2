import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='postgres_url')

    REDIS_HOST: str = Field(env='REDIS_HOST')
    REDIS_PORT: int = Field(env='REDIS_PORT')
    REDIS_DB: int = Field(env='REDIS_DB')

    class Config:
        env_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        )