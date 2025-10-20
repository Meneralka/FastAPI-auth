from typing import Annotated, Literal

from fastapi import Depends, Request
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

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


class TokenPayloadGetter:
    def __init__(self, token_type: Literal["access", "refresh"] = ACCESS_TOKEN_TYPE):
        self.token_type = token_type + "_token"

    async def __call__(self, request: Request) -> dict:
        token = request.cookies.get(self.token_type)
        if not token:
            raise TokenUnidentifiedException
        try:
            payload = auth_utils.decode_jwt(token=token)
        except InvalidTokenError:
            raise InvalidTokenException
        return payload


def get_user_by_token_of_type(token_type: Literal["access", "refresh"]):
    async def get_user_by_token_sub(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        payload: dict = Depends(TokenPayloadGetter(token_type)),
    ) -> User:

        validate_token_type(payload=payload, got_token_type=token_type)

        session_info = await get_session_info(
            session=session, uuid=payload.get("session_uuid")
        )
        if session_info is None:
            raise TokenExpiredException
        if session_info.status not in (SessionStatus.ACTIVE, 'active'):
            raise TokenExpiredException

        user = await get_user_by_id(
            session=session,
            id_=payload.get("sub"),
        )
        return user

    return get_user_by_token_sub


get_current_auth_user = get_user_by_token_of_type(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = get_user_by_token_of_type(REFRESH_TOKEN_TYPE)


async def get_session_info_from_payload(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    payload: dict = Depends(TokenPayloadGetter()),
):
    session_info = await get_session_info(
        session=session, uuid=payload.get("session_uuid")
    )

    if session_info is None:
        raise TokenExpiredException
    if session_info.status not in (SessionStatus.ACTIVE, 'active'):
        raise TokenExpiredException

    return session_info
