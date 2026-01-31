from src.exceptions.base import AppException


class ServerError(AppException):
    def __init__(self, status: int):
        super().__init__(
            message=f'Server error with status {status}',
            status_code=status
        )

