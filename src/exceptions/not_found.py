from starlette.status import HTTP_404_NOT_FOUND
from src.exceptions.base import AppException


class ObjectNotFound(AppException):

    def __init__(self, object_id: str | None = None):
        message = f"Object with id={object_id} not found" if object_id else "Object not found"
        super().__init__(
            message=message,
            status_code=HTTP_404_NOT_FOUND
        )