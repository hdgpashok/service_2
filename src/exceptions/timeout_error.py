from src.exceptions.base import AppException


class ServerTimeoutError(AppException):
    def __init__(self):
        super().__init__(
            message=f'Connection attempts have expired. The server crashes with error 504',
            status_code=504
        )

