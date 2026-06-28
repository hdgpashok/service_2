from fastapi import FastAPI, Request
from fastapi.responses import UJSONResponse
from redis import RedisError

from src.exceptions.base import AppException
from src.schemas.handler import Handler
from sqlalchemy.exc import SQLAlchemyError


def error_handler(app: FastAPI):
    @app.exception_handler(RedisError)
    async def redis_handler(request: Request, exc: RedisError):

        body = Handler(detail="Cache error")

        return UJSONResponse(
            status_code=500,
            content=body.model_dump()
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_handler(request: Request, exc: SQLAlchemyError):
        body = Handler(detail='Database error')

        return UJSONResponse(
            status_code=exc.status_code,
            content=body.model_dump()
        )

    @app.exception_handler(AppException)
    async def app_exceptions_handler(req: Request, exc: AppException):
        body = Handler(detail=exc.message)

        return UJSONResponse(
            status_code=exc.status_code,
            content=body.model_dump()
        )