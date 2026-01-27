import uuid

import httpx
import jwt
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from core.schemas.token import SessionCreate
from core.schemas.user import UserRead
from crud.tokens import create_session
from .helpers import create_access_token, create_refresh_token, validate_google_id

from jwt import PyJWKClient
import urllib.parse
from typing import Any, Annotated

from core.config import settings
from api.exceptions.auth import NoIdTokenException
from core.models import db_helper

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)


@router.get("/google")
def login_via_google():
    params = {
        "client_id": settings.google.client_id,
        "redirect_uri": settings.google.redirect_uri,
        "response_type": settings.google.response_type,
        "scope": settings.google.scope,
        "access_type": settings.google.access_type,
    }
    url = settings.google.authorize_url + "?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    response: Response,
    request: Request,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    token_json = await get_json_google_token(code)
    payload = get_google_user_payload(token_json)
    session_name = get_session_name(request)
    session_uuid = str(uuid.uuid4())
    google_user_id = payload["sub"]

    user = await validate_google_id(google_id=google_user_id, session=session)
    user = UserRead(**user.__dict__)

    user_session = SessionCreate(
        uuid=session_uuid,
        sub=user.id,
        name=session_name,
        ip=request.client.host,
    )
    got_session = await create_session(session, user_session)
    response = RedirectResponse(settings.google.redirect_after_auth_url)

    return await create_and_set_tokens_to_cookie(
        response=response, user=user, got_session=got_session
    )


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
