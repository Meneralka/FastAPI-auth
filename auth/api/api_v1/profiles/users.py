from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from core.schemas.user import UserReg, UserRead
from crud.users import get_all_users, create_user
from crud.users import create_user as db_create_user

router = APIRouter(tags=["Users"])


@router.get("", response_model=list[UserRead])
async def get_users(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    users = await get_all_users(session=session)
    return users


@router.post("", response_model=UserReg)
async def create_user(
    user: UserReg,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    new_user = await db_create_user(session, user)
    return new_user
