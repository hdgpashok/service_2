from functools import wraps
from typing import Callable

from src.exceptions.timeout_error import ServerTimeoutError
from src.services.timeout import timeout_with_jitter
from src.core.config import Settings


settings = Settings()


def retry(exceptions: tuple, max_retries: int = settings.MAX_RETRIES):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            for attempt in range(1, max_retries + 4):
                try:
                    await func(*args, **kwargs)
                except exceptions:
                    if attempt == settings.MAX_RETRIES:
                        raise ServerTimeoutError()

                await timeout_with_jitter(attempt)
        return inner

    return wrapper