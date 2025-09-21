import logging

from loguru import logger
import sys

from core.config import settings

logger.remove()

logger.add(
    sys.stderr,
    level=logging.DEBUG,
    format=settings.logs.cmd_format,
    colorize=True,
)

logger.add(
    settings.logs.auth_logs,
    level=logging.INFO,
    format=settings.logs.file_format,
    rotation=settings.logs.rotation,
    retention=settings.logs.retention,
    compression=settings.logs.compression,
)
logger.add(
    settings.logs.error_logs,
    level=logging.ERROR,
    format=settings.logs.file_format,
    rotation=settings.logs.rotation,
    retention=settings.logs.retention,
    compression=settings.logs.compression,
)
