import uuid

import httpx
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas.token import SessionCreate
from core.schemas.user import UserRead
from crud.tokens import create_session
from .helpers import create_access_token, create_refresh_token, validate_google_id

import urllib.parse
from typing import Any, Annotated

from core.config import settings
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
