from starlette.status import HTTP_504_GATEWAY_TIMEOUT
from src.exceptions.base import AppException


class ServerTimeoutError(AppException):
    def __init__(self, message: str = "Service timeout"):
        super().__init__(
            message=message,
            status_code=HTTP_504_GATEWAY_TIMEOUT
        )