
import random

import asyncio


async def timeout_with_jitter(attempt: int):
    delay = 0.1 * (2 ** attempt)
    jitter = random.uniform(0, delay * 0.3)
    await asyncio.sleep(delay + jitter)