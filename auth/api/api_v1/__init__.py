from fastapi import APIRouter

from core.config import settings

from .authentication.jwt_auth import router as auth_router
from .authentication.google import router as google_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(
    auth_router,
)

router.include_router(
    google_router,
)
