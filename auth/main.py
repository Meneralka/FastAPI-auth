from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import settings

from api import router as api_router
from core.models import db_helper
from logs import logger  # noqa: F401
from api.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    # faststream broker

    yield

    # shutdown
    # faststream broker
    await db_helper.dispose()


main_app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
register_exception_handlers(main_app)
main_app.include_router(
    api_router,
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app", host=settings.run.host, port=settings.run.port, reload=True
    )
