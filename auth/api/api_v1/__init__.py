from fastapi import APIRouter

from core.config import settings

from .authentication.jwt_auth import router as auth_router
from .authentication.register import router as register_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(
    auth_router,
)

router.include_router(
    register_router,
)
