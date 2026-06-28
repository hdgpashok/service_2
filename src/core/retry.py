import logging
from typing import Callable, Any
from functools import wraps

from src.core.config import settings
from src.core.logger import get_logger
from src.core.timeout import timeout_with_jitter
from src.exceptions.timeout_error import ServerTimeoutError


logger = get_logger('retry_logger')


RETRY_STATUSES = [500, 502, 503, 504, 408, 409, 429]

logger = logging.getLogger("retry_logger")


def retry(
        max_retries: int | None = None,
        retry_if_result: Callable[[Any], bool] | None = None,
        retry_exceptions: tuple = (),
):
    if max_retries is None:
        max_retries = settings.MAX_RETRIES

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            last_result = None

            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    last_result = result

                    if retry_if_result is not None:
                        try:
                            should_retry = retry_if_result(result)
                        except Exception as e:
                            logger.warning(f"[{func.__name__}] Error in retry_if_result: {e}")
                            should_retry = False

                        if should_retry:
                            if attempt == max_retries - 1:
                                status_code = getattr(result, 'status_code', 'N/A')
                                logger.error(
                                    f"[{func.__name__}] All {max_retries} attempts exhausted. "
                                    f"Last status code: {status_code}"
                                )
                                break

                            logger.warning(
                                f"[{func.__name__}] Attempt {attempt + 1}/{max_retries} | "
                                f"Received status for retry: {getattr(result, 'status_code', 'N/A')}"
                            )
                            await timeout_with_jitter(attempt)
                            continue

                    return result

                except retry_exceptions as exc:
                    last_exception = exc
                    if attempt == max_retries - 1:
                        logger.error(
                            f"[{func.__name__}] All {max_retries} attempts exhausted with exception: {type(exc).__name__}"
                        )
                        break

                    logger.warning(
                        f"[{func.__name__}] Attempt {attempt + 1}/{max_retries} | "
                        f"Exception: {type(exc).__name__} - retrying..."
                    )
                    await timeout_with_jitter(attempt)

            if last_exception:
                logger.error(f"[{func.__name__}] Raising ServerTimeoutError after {max_retries} attempts")
                raise ServerTimeoutError(
                    message=f"External service request failed after {max_retries} attempts. "
                            f"Last error: {type(last_exception).__name__}"
                ) from last_exception

            raise ServerTimeoutError(
                message=f"[{func.__name__}] Unknown failure after {max_retries} attempts"
            )

        return wrapper

    return decorator