from fastapi import FastAPI, Request
from fastapi.responses import UJSONResponse
from exceptions.base import AppException


def error_handler(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exceptions_handler(req: Request, exc: AppException):
        body = {'detail': exc.message}

        return UJSONResponse(
            status_code=exc.status_code,
            content=body
        )