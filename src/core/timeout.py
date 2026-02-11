from src.core.config import Settings

from src.core.logger import get_logger

import random

import asyncio


settings = Settings()


async def timeout_with_jitter(attempt: int):
    delay = 0.1 * (2 ** attempt)
    jitter = random.uniform(0, delay * 0.3)
    await asyncio.sleep(delay + jitter)