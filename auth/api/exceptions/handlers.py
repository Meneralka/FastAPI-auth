from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import IntegrityError, DBAPIError
from starlette import status
from loguru import logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        logger.error("Error integrity error: %s" % exc)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Oops! Unknown error"},
        )

    @app.exception_handler(DBAPIError)
    async def handle_db_error(request: Request, exc: DBAPIError):
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Oops! Invalid value"},
        )

