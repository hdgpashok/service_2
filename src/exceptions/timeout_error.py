from src.exceptions.base import AppException


class ServerTimeoutError(AppException):
    def __init__(self):
        super().__init__(
            message=f'Server timeout error. Status code = 504',
            status_code=504
        )

