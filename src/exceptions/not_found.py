from src.exceptions.base import AppException
from sqlalchemy import UUID


class ObjectNotFound(AppException):
    def __init__(self, object_id: UUID):
        super().__init__(
            message=f'Object with {object_id} not found',
            status_code=404
        )

