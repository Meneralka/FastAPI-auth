import uuid

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import declared_attr
from sqlalchemy import MetaData
from sqlalchemy.types import UUID

from core.config import settings
from utils import camel_case_to_snake_case


def get_uuid_str():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=get_uuid_str,
    )
