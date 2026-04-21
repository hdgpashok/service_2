from uuid import UUID

import httpx
import ujson

from src.schemas.user import UserExternal
from src.core.config import Settings
from src.core.logger import get_logger
from src.core.retry import retry
from src.core.redis_cache import CacheService
from src.exceptions.not_found import ObjectNotFound

from starlette.status import HTTP_404_NOT_FOUND


logger = get_logger('call_api_logger')

settings = Settings()


class ClientMainService:
    def __init__(self, cache: CacheService):
        self.client = httpx.AsyncClient(
            base_url=settings.service1_base_url,
            timeout=settings.HTTP_TIMEOUT,
        )
        self.cache = cache

    @retry()
    async def user_get_request(self, user_id: UUID):
        key = f'user:{user_id}'

        logger.info(f'[GET USER] Start request user_id={user_id}')

        cache_data = await self.cache.get(key)
        if cache_data is not None:
            logger.info(f'[GET USER] Cache hit user_id={user_id}')
            return cache_data

        resp = await self.client.get(f"/users/{user_id}")

        logger.info(
            f'[GET USER] Response received user_id={user_id} '
            f'status_code={resp.status_code}'
        )

        if resp.status_code == HTTP_404_NOT_FOUND:
            logger.warning(f'[GET USER] Not found user_id={user_id}')
            raise ObjectNotFound(object_id=user_id)

        data = ujson.loads(resp.text)

        logger.info(f'[GET USER] Caching user user_id={user_id}')
        await self.cache.set(key, data, expire=3600)

        logger.info(f'[GET USER] Success user_id={user_id}')
        return data

    @retry()
    async def user_post_request(self, user: UserExternal):
        logger.info(f'[POST USER] Start request user_id={user.id}')

        resp = await self.client.post(
            f"{settings.service1_base_url}/external_user",
            json=user.model_dump(mode='json')
        )

        logger.info(
            f'[POST USER] Response received user_id={user.id} '
            f'status_code={resp.status_code}'
        )

        logger.info(f'[POST USER] Success user_id={user.id}')

    @retry()
    async def user_delete_request(self, user_id: UUID):
        logger.info(f'[DELETE USER] Start request user_id={user_id}')

        try:
            resp = await self.client.delete(
                f'{settings.service1_base_url}/users/{user_id}'
            )

        except Exception as delete_exc:
            logger.critical(
                f'[CREATE USER] CRITICAL: Failed to rollback external user! '
                f'user_id={user_id} error={repr(delete_exc)}'
            )

        logger.info(f'[DELETE USER] Success user_id={user_id}')