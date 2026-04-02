from src.exceptions.base import AppException

from starlette.status import HTTP_504_GATEWAY_TIMEOUT


class ServerTimeoutError(AppException):
    def __init__(self):
        super().__init__(
            message=f'Connection attempts have expired. The server crashes with error 504',
            status_code=HTTP_504_GATEWAY_TIMEOUT
        )

