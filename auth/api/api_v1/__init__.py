from fastapi import APIRouter

from core.config import settings

from .profiles.users import router as users_router
from .authentication.jwt_auth import router as demo_auth_router
from .authentication.register import router as register_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(
    users_router,
    prefix=settings.api.v1.users,
)
router.include_router(
    demo_auth_router,
)

router.include_router(
    register_router,
)
