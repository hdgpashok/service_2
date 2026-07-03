from uuid import UUID

import httpx
import ujson

from src.schemas.user import UserExternal
from src.utils.config import settings
from src.utils.logger import get_logger
from src.utils.retry import retry, RETRY_STATUSES
from src.exceptions.not_found import ObjectNotFound

from starlette.status import HTTP_404_NOT_FOUND


logger = get_logger('call_api_logger')


class ClientUserService:
    def __init__(self, base_url: str = None):
        self.client = httpx.AsyncClient(
            base_url=base_url or settings.service1_base_url,
            timeout=settings.HTTP_TIMEOUT,
        )

    @retry(
        retry_if_result=lambda resp: (
                isinstance(resp, httpx.Response) and resp.status_code in RETRY_STATUSES
        ),
        retry_exceptions=(httpx.TimeoutException, httpx.ConnectError),
    )
    async def user_get_request(self, user_id: UUID):

        resp: httpx.Response = await self.client.get(f"/users/{user_id}")

        if resp.status_code == HTTP_404_NOT_FOUND:
            logger.warning(f'[GET USER] Not found user_id={user_id}')
            raise ObjectNotFound(object_id=user_id)

        logger.info(
            f'[GET USER] Response received user_id={user_id} '
            f'status_code={resp.status_code}'
        )

        data = ujson.loads(resp.text)

        logger.info(f'[GET USER] Success user_id={user_id}')
        return data

    @retry(
        retry_if_result=lambda resp: (
                isinstance(resp, httpx.Response) and resp.status_code in RETRY_STATUSES
        ),
        retry_exceptions=(httpx.TimeoutException, httpx.ConnectError),
    )
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

    @retry(
        retry_if_result=lambda resp: (
                isinstance(resp, httpx.Response) and resp.status_code in RETRY_STATUSES
        ),
        retry_exceptions=(httpx.TimeoutException, httpx.ConnectError),
    )
    async def user_delete_request(self, user_id: UUID):
        logger.info(f'[DELETE USER] Start request user_id={user_id}')

        try:
            await self.client.delete(
                f'{settings.service1_base_url}/users/{user_id}'
            )

        except Exception as delete_exc:
            logger.critical(
                f'[CREATE USER] CRITICAL: Failed to rollback external user! '
                f'user_id={user_id} error={repr(delete_exc)}'
            )

        logger.info(f'[DELETE USER] Success user_id={user_id}')