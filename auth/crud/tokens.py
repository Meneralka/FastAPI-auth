from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions.auth import SessionNotFound
from core.models.user import Session, SessionStatus

from core.schemas.token import SessionCreate, SessionRead
from core.redis.cache import Cache


@Cache.redis(read=True, namespace="sessions", model_class=SessionRead)
async def get_same_session(
        session: AsyncSession,
        new_session: SessionCreate,
) -> Session:
    stmt = select(Session).where(
        Session.sub == new_session.sub,
        Session.ip == new_session.ip,
        Session.name == new_session.name,
    ).order_by(Session.id)

    result = await session.scalar(stmt)
    return result


@Cache.redis(write=True, namespace="sessions")
async def create_session(
        session: AsyncSession,
        new_session: SessionCreate,
):
    """
    Создаёт новую сессию если не находит похожей уже существующей.
    Похожей сессия считается, если у них совпадает:
    - name (user-agent),
    - ip (ip-address),
    - Айди пользователя
    """
    if got_session := await get_same_session(session, new_session):
        new_session.uuid = got_session.uuid
        stmt = (
            update(Session)
            .where(Session.uuid == new_session.uuid)
            .values(status=SessionStatus.ACTIVE)
        )
        await session.execute(stmt)
    else:
        new_session = Session(**new_session.model_dump())
        session.add(new_session)
    await session.commit()
    return new_session


@Cache.redis(read=True, namespace="sessions", model_class=SessionRead)
async def get_user_sessions(
        session: AsyncSession,
        sub_id: str,
) -> Sequence[Session]:
    stmt = (
        select(Session)
        .where(Session.sub == sub_id)
        .order_by(Session.timestamp)
    )
    result = await session.scalars(stmt)
    return result.all()


@Cache.redis(read=True, namespace="sessions", model_class=SessionRead)
async def get_session_info(
        session: AsyncSession,
        uuid: str,
) -> Session:
    stmt = select(Session).where(
        Session.uuid == uuid,
        Session.status == SessionStatus.ACTIVE
    )
    result = await session.scalars(stmt)
    return result.one_or_none()


@Cache.redis(write=True, namespace="sessions")
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


@Cache.redis(write=True, namespace="sessions")
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
