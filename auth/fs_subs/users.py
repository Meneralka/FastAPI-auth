from faststream.nats import NatsRouter
from loguru import logger as log

router = NatsRouter()


@router.subscriber("user-register")
async def send_welcome_message(username) -> str:
    """
    Sends a welcome message to the user.
    """
    log.info("User registered %s", username)
    return username
