from src.core.config import Settings

from src.core.logger import get_logger

import random

import asyncio


logger = get_logger('timeout_logger')
settings = Settings()


async def timeout_with_jitter(attempt: int):
    delay = 0.1 * (2 ** attempt)
    jitter = random.uniform(0, delay * 0.3)
    logger.info(f'attempt №{attempt + 1} delay {delay + jitter}')
    await asyncio.sleep(delay + jitter)