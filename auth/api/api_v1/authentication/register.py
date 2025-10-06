from typing import Annotated

from fastapi import Depends, APIRouter, Form
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper

from core.schemas.user import UserReg, UserBase
from crud.users import create_user as db_create_user
from utils import auth as auth_utils
from loguru import logger as log

router = APIRouter(
    prefix=settings.api.v1.register_,
    tags=["Register"],
)


def validate_register_form(username: str = Form(), password: str = Form()) -> UserReg:
    return UserReg(
        username=username, hashed_password=auth_utils.hash_password(password)
    )


@router.post("", response_model=UserBase)
async def register_user(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: UserReg = Depends(validate_register_form),
):

    new_user = await db_create_user(session, user)
    log.info(
        "[REGISTER] New user: %(username)s with id: %(id)s"
        % {"username": user.username, 'id': new_user.id},
    )
    return new_user
