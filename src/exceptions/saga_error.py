from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT
from src.exceptions.base import AppException


class SagaError(AppException):
    def __init__(self, message: str = "Saga rollback"):
        super().__init__(
            message=message,
            status_code=HTTP_422_UNPROCESSABLE_CONTENT
        )