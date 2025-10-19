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
) -> str:
    jwt_payload = payload.copy()
    jwt_payload.update({TOKEN_TYPE_FIELD: token_type})
    token = auth_utils.encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )
    return token


class CreateToken:
    def __init__(self, token_type: str) -> None:
        self.token_type = token_type

    async def __call__(
            self,
            user: UserAuth,
            session_uuid: str,
    ) -> str:
        jwt_payload = {
            "sub": user.id,
            "username": user.username,
            "session_uuid": session_uuid,
        }
        log.info(
            "[CREATE TOKEN] for %(user)s - (session_uuid=%(session_uuid)s)"
            % {"user": user.id, "session_uuid": session_uuid}
        )
        if self.token_type == ACCESS_TOKEN_TYPE:
            expire_timedelta = timedelta(
                minutes=settings.auth.access_token_expire_minutes
            )
        else:
            expire_timedelta = timedelta(
                days=settings.auth.refresh_token_expire_days
            )

        return create_jwt(
            token_type=self.token_type,
            payload=jwt_payload,
            expire_timedelta=expire_timedelta,
        )


async def validate_and_get_user(
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
    if not auth_utils.validate_password(
            password=password, hashed_password=user.hashed_password
    ):
        log.info(
            "[TRY TO LOGIN] failed attempt from %(ip)s for user %(username)s"
            % {"username": username, "ip": request.client.host}
        )
        raise InvalidCredentialsException

    return user


create_access_token = CreateToken(ACCESS_TOKEN_TYPE)
create_refresh_token = CreateToken(REFRESH_TOKEN_TYPE)
