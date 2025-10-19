from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError
from loguru import logger as logs

from api.exceptions.auth import (
    ValueAlreadyExistsException,
    DatabaseError,
    InvalidCredentialsException,
)
from core.models import User
from core.schemas.user import UserReg, UserRead, UserAuth
from core.redis.cache import Cache


async def get_all_users(
    session: AsyncSession,
) -> Sequence[User]:
    stmt = select(User).order_by(User.id)
    result = await session.scalars(stmt)
    return result.all()


@Cache.redis(read=True, namespace="users", model_class=UserAuth)
async def get_user_by_username(
    session: AsyncSession,
    username: str,
) -> User:
    stmt = select(User).where(User.username == username)
    result = await session.scalars(stmt)
    return result.first()

@Cache.redis(read=True, namespace="users", model_class=UserRead)
async def get_user_by_id(
    session: AsyncSession,
    id_: str,
) -> User:
    stmt = select(User).where(User.id == id_)
    result = await session.scalars(stmt)
    return result.first()

async def create_user(session: AsyncSession, user_create: UserReg) -> User:
    user = User(**user_create.model_dump())
    session.add(user)
    try:
        await session.commit()
        # await session.refresh(user)

    except IntegrityError as e:
        if e.orig.__cause__.__class__ == UniqueViolationError:
            raise ValueAlreadyExistsException
        raise DatabaseError
    return user
