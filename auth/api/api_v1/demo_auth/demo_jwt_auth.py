import uuid
from datetime import datetime, timedelta, UTC

from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Response, Request, Form
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger as log
from user_agents import parse

from core.schemas.token import Tokens, SessionCreate, SessionRead
from crud.tokens import (
    create_session,
    abort_session,
    get_user_sessions,
    abort_another_session,
)
from .helpers import create_access_token, create_refresh_token, validate_auth_user
from core.config import settings
from core.schemas.user import UserRead
from core.models import db_helper
from .validation import (
    get_current_auth_user_for_refresh,
    get_current_auth_user,
    http_bearer,
    get_session_uuid_from_payload,
    get_session_info_from_payload,
)
from api.exceptions.auth import NeedMorePermission

router = APIRouter(
    prefix=settings.api.v1.demo_auth,
    tags=["Auth"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/login", response_model=Tokens)
async def auth_user_issue_jwt(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    response: Response,
    request: Request,
    user: UserRead = Depends(validate_auth_user),
):
    session_uuid = str(uuid.uuid4())
    user_agent_str = parse(request.headers.get("User-Agent", "Unknown"))
    session_name = (
        f"{user_agent_str.browser.family} {user_agent_str.browser.version_string},"
        f" {user_agent_str.os.family} {user_agent_str.os.version_string}"
    )

    user_session = SessionCreate(
        uuid=session_uuid,
        sub=str(user.id),
        name=session_name,
    )
    await create_session(session, user_session)

    access_token = create_access_token(
        user=user,
        sui=session_uuid,
    )
    refresh_token = create_refresh_token(
        user=user,
        sui=session_uuid,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.auth.refresh_token_expire_days * 30 * 24 * 60,
        secure=True,
        httponly=True,
    )
    log.info(
        "[%(ip)s] [LOGIN] access_token %(user)s (id=%(id)s)"
        % {"ip": request.client.host, "user": user.username, "id": user.id},
    )
    return Tokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Tokens, response_model_exclude_none=True)
async def auto_refresh_jwt(
    request: Request,
    user: UserRead = Depends(get_current_auth_user_for_refresh),
    sui: str = Depends(get_session_uuid_from_payload),
):
    access_token = create_access_token(
        user=user,
        sui=sui,
    )
    log.info(
        "[%(ip)s] [REFRESH] access_token %(user)s (id=%(id)s)"
        % {"ip": request.client.host, "user": user.username, "id": user.id},
    )
    return Tokens(
        access_token=access_token,
    )


@router.post("/logout", response_model_exclude_none=True)
async def logout_user(
    response: Response,
    request: Request,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    session_data: SessionRead = Depends(get_session_info_from_payload),
):
    await abort_session(session=session, uuid=session_data.uuid)
    response.delete_cookie(
        key="refresh_token",
        secure=True,
        httponly=True,
    )
    log.info(
        "[%(ip)s] [LOGOUT] session %(sui)s (id=%(id)s)"
        % {
            "ip": request.client.host,
            "id": session_data.uuid,
            "sui": session_data.uuid,
        },
    )
    return ORJSONResponse({"success": True})


@router.post("/abort")
async def abort_user_session(
    request: Request,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    session_data: SessionRead = Depends(get_session_info_from_payload),
    sui: str = Form(),
):

    if not session_data.can_abort:
        raise NeedMorePermission

    await abort_another_session(
        session=session, current_user_uuid=session_data.sub, uuid=sui
    )
    log.info(
        "[%(ip)s] [ABORT SESSION] session %(sui)s (id=%(id)s)"
        % {
            "ip": request.client.host,
            "id": sui,
            "sui": session_data.sub,
        },
    )
    return ORJSONResponse({"success": True})


@router.get("/sessions", response_model=Sequence[SessionRead])
async def get_sessions(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: UserRead = Depends(get_current_auth_user),
):
    sessions: Sequence[SessionRead] = await get_user_sessions(
        session, sub_id=str(user.id)
    )
    return sessions
