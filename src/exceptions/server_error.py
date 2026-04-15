from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from src.exceptions.base import AppException


class ServerError(AppException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            message=message,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )