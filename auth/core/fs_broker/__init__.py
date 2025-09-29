__all__ = ("broker",)

from faststream.nats import NatsBroker

from core.config import settings
from fs_subs.users import router

broker = NatsBroker(
    settings.faststream.nats.url,
)

broker.include_router(router)
