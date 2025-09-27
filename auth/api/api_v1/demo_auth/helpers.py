from datetime import timedelta
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Form, Depends, Request
from loguru import logger as log

from api.exceptions.auth import InvalidCredentialsException

from core.config import (
    settings,
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from core.models import User, db_helper
from core.schemas.user import UserAuth
from crud.users import get_user_by_username
from utils import auth as auth_utils


def create_jwt(
    token_type: str,
    payload: dict,
    expire_timedelta: timedelta | None = None,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
) -> str:
    jwt_payload = payload.copy()
    jwt_payload.update({TOKEN_TYPE_FIELD: token_type})
    token = auth_utils.encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )
    return token


def create_token_factory(token_type: str):
    def create_token(
        user: UserAuth,
        session_uuid: str | None = None,
    ) -> str:
        jwt_payload = {"sub": user.id, "username": user.username, "session_uuid": session_uuid}
        log.info(
            "[CREATE TOKEN] for %(user)s - (session_uuid=%(session_uuid)s)"
            % {"user": user.id, "session_uuid": session_uuid}
        )
        return create_jwt(
            token_type=token_type,
            payload=jwt_payload,
            expire_timedelta=timedelta(
                minutes=settings.auth.access_token_expire_minutes
            ),
        )

    return create_token


async def validate_auth_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    request: Request,
    username: str = Form(),
    password: str = Form(),
) -> User:
    user = await get_user_by_username(session=session, username=username)
    if not user:
        log.info(
            "[TRY TO LOGIN] invalid username %(username)s from %(ip)s"
            % {"username": username[:20], "ip": request.client.host}
        )
        raise InvalidCredentialsException
    if auth_utils.validate_password(
        password=password, hashed_password=user.hashed_password
    ):
        return user
    log.info(
        "[TRY TO LOGIN] failed attempt from %(ip)s for user %(username)s"
        % {"username": username, "ip": request.client.host}
    )
    raise InvalidCredentialsException


create_access_token = create_token_factory(ACCESS_TOKEN_TYPE)
create_refresh_token = create_token_factory(REFRESH_TOKEN_TYPE)
