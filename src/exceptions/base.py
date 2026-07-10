from fastapi import status as http_status


class AppException(Exception):
    def __init__(
            self,
            message: str,
            status_code: int = http_status.HTTP_400_BAD_REQUEST,
            detail: str | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)