from uuid import UUID

import httpx

from src.schemas.user import UserExternal
from src.core.config import Settings
from src.core.logger import get_logger
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
    async def user_get_request(user_id: UUID):
        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                resp = await client.get(f'/users/{user_id}')
                if resp.status_code == 404:
                    raise ObjectNotFound(object_id=user_id)

                if resp.status_code >= 500:
                    raise
                return resp.json()

            except (
                    httpx.TimeoutException,
                    httpx.ConnectError,
                    httpx.HTTPStatusError,
            ) as exc:

                await timeout_with_jitter(attempt)

    @staticmethod
    async def user_post_request(user: UserExternal):
        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                await client.post(
                    f"{settings.service1_base_url}/external_user",
                    json=user.model_dump(mode='json')
                )
                break

            except Exception as e:
                await timeout_with_jitter(attempt)
