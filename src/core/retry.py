from functools import wraps

from src.exceptions.timeout_error import ServerTimeoutError
from src.core.timeout import timeout_with_jitter
from src.core.config import Settings

from src.core.logger import get_logger


logger = get_logger('retry_logger')

settings = Settings()


def retry(exceptions: tuple, max_retries: int = settings.MAX_RETRIES):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except exceptions:
                    if attempt == max_retries:
                        logger.error('Attempts are over. Throwing server error.')
                        raise ServerTimeoutError()

                logger.info(f'Attempt number {attempt} failed. Trying one more time.')
                await timeout_with_jitter(attempt)
        return inner

    return wrapper