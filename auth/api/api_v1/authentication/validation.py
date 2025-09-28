from typing import Annotated, Literal

from fastapi import Depends, Request
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger as log

from api.exceptions.auth import (
    InvalidTokenException,
    TokenUnidentifiedException,
    TokenExpiredException,
)

from core.models import db_helper
from crud.tokens import get_session_info
from crud.users import get_user_by_id
from utils.auth import validate_token_type
from core.config import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from utils import auth as auth_utils
from core.models.user import SessionStatus, User

http_bearer = HTTPBearer(auto_error=False)


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    if credentials:
        token = str(credentials.credentials)
    else:
        raise TokenUnidentifiedException
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError:
        raise InvalidTokenException
    return payload


def get_user_by_token_of_type(token_type: str):
    async def get_user_by_token_sub(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        payload: dict = Depends(get_current_token_payload),
    ) -> User:
        validate_token_type(payload=payload, got_token_type=token_type)
        session_info = await get_session_info(session=session, uuid=payload.get("session_uuid"))

        if session_info is None:
            raise TokenExpiredException
        if session_info.status != SessionStatus.ACTIVE:
            raise TokenExpiredException

        user = await get_user_by_id(
            session=session,
            id_=payload.get("sub"),
        )
        return user

    return get_user_by_token_sub


get_current_auth_user = get_user_by_token_of_type(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = get_user_by_token_of_type(REFRESH_TOKEN_TYPE)


def get_session_uuid_from_payload(
    payload: dict = Depends(get_current_token_payload),
):
    return payload.get("session_uuid")


async def get_session_info_from_payload(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    payload: dict = Depends(get_current_token_payload),
):
    session_info = await get_session_info(session=session, uuid=payload.get("session_uuid"))

    if session_info is None:
        raise TokenExpiredException
    if session_info.status != SessionStatus.ACTIVE:
        raise TokenExpiredException

    return session_info
