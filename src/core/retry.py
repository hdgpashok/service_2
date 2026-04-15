from functools import wraps
from typing import Callable


from src.core.config import Settings
from src.core.logger import get_logger
from src.core.timeout import timeout_with_jitter
from src.exceptions.timeout_error import ServerTimeoutError


logger = get_logger('retry_logger')
settings = Settings()

RETRY_STATUSES = [500, 502, 503, 504, 429]


def retry(max_retries: int | None = None):
    if max_retries is None:
        max_retries = settings.MAX_RETRIES

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except Exception as exc:
                    logger.warning(
                        f"[RETRY] Attempt {attempt + 1}/{max_retries} failed "
                        f"with {type(exc).__name__}. Retrying..."
                        f"{exc}"
                    )
                    if attempt == max_retries - 1:
                        break
                    await timeout_with_jitter(attempt)

            logger.error(f"[RETRY] All {max_retries} attempts failed")
            raise ServerTimeoutError()

        return wrapper

    return decorator