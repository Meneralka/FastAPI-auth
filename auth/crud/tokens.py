from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions.auth import SessionNotFound
from core.models.user import Session, SessionStatus

from core.schemas.token import SessionCreate


async def create_session(
    session: AsyncSession,
    new_session: SessionCreate,
):
    new_session = Session(**new_session.model_dump())
    session.add(new_session)
    await session.commit()


async def get_user_sessions(
    session: AsyncSession,
    sub_id: str,
):
    stmt = select(Session).where(Session.sub == sub_id)
    result = await session.scalars(stmt)
    return result.all()


async def get_session_info(
    session: AsyncSession,
    uuid: str,
):
    stmt = select(Session).where(
        Session.uuid == uuid, Session.status == SessionStatus.ACTIVE
    )
    result = await session.scalars(stmt)
    return result.one_or_none()


async def abort_session(
    session: AsyncSession,
    uuid: str,
):
    stmt = (
        update(Session)
        .where(Session.uuid == uuid)
        .values(status=SessionStatus.DISABLED)
    )
    await session.execute(stmt)
    await session.commit()


async def abort_another_session(
    session: AsyncSession,
    current_user_uuid: str,
    uuid: str,
):
    stmt = (
        update(Session)
        .where(
            Session.uuid == uuid,
            Session.sub == current_user_uuid,
        )
        .values(status=SessionStatus.DISABLED)
        .returning(Session)
    )
    result = await session.execute(stmt)
    updated = result.one_or_none()
    if updated:
        await session.commit()
        return updated
    raise SessionNotFound
