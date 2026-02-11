import json
from uuid import UUID

import httpx
import ujson

from fastapi.responses import UJSONResponse

from src.schemas.user import UserExternal
from src.core.config import Settings
from src.core.logger import get_logger
from src.core.retry import retry
from src.core.redis_cache import rd, expire_time

from src.exceptions.server_error import ServerError
from src.exceptions.not_found import ObjectNotFound


logger = get_logger('call_api_logger')

settings = Settings()


class Client:

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.service1_base_url,
            timeout=settings.HTTP_TIMEOUT,
        )

    @retry(exceptions=(ServerError, httpx.ConnectTimeout))
    async def user_get_request(self, user_id: UUID):
        key = f'user:{user_id}'
        cache = await rd.get(key)

        if cache:
            logger.info(f'cache hit, user with id {user_id} already cached')
            return ujson.loads(cache)

        else:
            resp = await self.client.get(f"/users/{user_id}")

            if resp.status_code >= 500:
                raise ServerError(resp.status_code)

            if resp.status_code == 404:
                raise ObjectNotFound(object_id=user_id)

            logger.info(f'caching user with id {user_id}')

            await rd.set(key, json.dumps(resp.json()), ex=expire_time)
            return ujson.loads(json.dumps(resp.json()))

    @retry(exceptions=(ServerError, httpx.ConnectTimeout))
    async def user_post_request(self, user: UserExternal):
        resp = await self.client.post(
            f"{settings.service1_base_url}/external_user",
            json=user.model_dump(mode='json')
        )

        if resp.status_code >= 500:
            raise ServerError(resp.status_code)

    @retry(exceptions=(ServerError, httpx.ConnectTimeout))
    async def user_delete_request(self, user_id: UUID):
        resp = await self.client.delete((
            f'{settings.service1_base_url}/users/{user_id}'
        ))

        if resp.status_code >= 500:
            raise ServerError(resp.status_code)

        if resp.status_code == 404:
            raise ObjectNotFound(object_id=user_id)
