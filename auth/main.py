from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from core.config import settings

from api import router as api_router
from core.models import db_helper
from core.redis import RedisClient
from logs import logger  # noqa: F401
from api.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициировать подключение в этом месте не требуется
    yield
    await RedisClient.close()
    await db_helper.dispose()


main_app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
register_exception_handlers(main_app)
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
main_app.include_router(
    api_router,
)
