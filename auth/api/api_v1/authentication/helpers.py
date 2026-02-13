from datetime import timedelta
from typing import Annotated, Any

import jwt
from jwt import PyJWKClient

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Form, Depends, Request
from loguru import logger as log
from starlette.requests import Request
from starlette.responses import Response
from user_agents import parse

from api.exceptions.auth import InvalidCredentialsException, NoIdTokenException

from core.config import (
    settings,
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from core.models import User, db_helper
from core.schemas.user import UserAuth, UserReg, UserRead
from crud.users import get_user_by_username, create_user
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
            expire_timedelta = timedelta(days=settings.auth.refresh_token_expire_days)

        return create_jwt(
            token_type=self.token_type,
            payload=jwt_payload,
            expire_timedelta=expire_timedelta,
        )


async def validate_google_id(
    google_id: str, session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
) -> User:
    user = await get_user_by_username(session=session, username=google_id)
    if not user:
        user_schema = UserReg(username=google_id)
        user = await create_user(session, user_schema)
    return user


create_access_token = CreateToken(ACCESS_TOKEN_TYPE)
create_refresh_token = CreateToken(REFRESH_TOKEN_TYPE)


async def create_and_set_tokens_to_cookie(
    response: Response, user: UserRead, got_session: Any
):
    access_token = await create_access_token(
        user=user,
        session_uuid=got_session.uuid,
    )
    refresh_token = await create_refresh_token(
        user=user,
        session_uuid=got_session.uuid,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.auth.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=True,
    )

    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.auth.access_token_expire_minutes * 60,
        httponly=True,
        secure=True,
    )
    return response


async def get_json_google_token(code: str):
    data = {
        "code": code,
        "client_id": settings.google.client_id,
        "client_secret": settings.google.client_secret,
        "redirect_uri": settings.google.redirect_uri,
        "grant_type": settings.google.grant_type,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(settings.google.token_url, data=data)
        token_json = token_response.json()

        return token_json


def get_google_user_payload(token_json: Any):
    id_token = token_json.get("id_token")
    if not id_token:
        raise NoIdTokenException

    jwk_client = PyJWKClient(settings.google.jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(id_token)
    payload = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=[settings.google.algorithm],
        audience=settings.google.client_id,
        issuer=["https://accounts.google.com", "accounts.google.com"],
    )

    return payload


def get_session_name(request: Request) -> str:
    user_agent_str = parse(request.headers.get("User-Agent", "Unknown"))
    session_name = (
        f"{user_agent_str.browser.family} {user_agent_str.browser.version_string},"
        f" {user_agent_str.os.family} {user_agent_str.os.version_string}"
    )
    return session_name
