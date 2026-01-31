from uuid import UUID

import httpx

from src.schemas.user import UserExternal
from src.core.config import Settings
from src.core.logger import get_logger
from src.core.retry import retry

from src.exceptions.server_error import ServerError
from src.exceptions.timeout_error import ServerTimeoutError
from src.exceptions.not_found import ObjectNotFound

from src.services.timeout import timeout_with_jitter

logger = get_logger('call_api_logger')

settings = Settings()

client = httpx.AsyncClient(
    base_url=settings.service1_base_url,
    timeout=settings.HTTP_TIMEOUT,
)


class CallApi:

    @staticmethod
    @retry(exceptions=(ServerError, httpx.ConnectTimeout))
    async def user_get_request(user_id: UUID):
        resp = await client.get(f"/users/{user_id}")

        if resp.status_code in (500, 502, 503, 504):
            raise ServerError(resp.status_code)

        if resp.status_code == 404:
            raise ObjectNotFound(object_id=user_id)

        return resp.json()

    @staticmethod
    @retry(exceptions=(ServerError, httpx.ConnectTimeout))
    async def user_post_request(user: UserExternal):
        await client.post(
            f"{settings.service1_base_url}/external_user",
            json=user.model_dump(mode='json')
        )
