import os
from typing import ClassVar

import httpx

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='postgres_url')
    service1_base_url: str = Field(env='service1_base_url')

    MAX_RETRIES: int = Field(env='MAX_RETRIES')

    HTTP_TIMEOUT: ClassVar[httpx.Timeout] = httpx.Timeout(
        connect=1.0,
        read=3.0,
        write=3.0,
        pool=1.0,
    )

    class Config:
        env_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        )