import os, jwt, json, string, secrets, functools

from sqlalchemy import and_, true, false
from sqlalchemy.future import select


from participant.models import PersonParticipant


async def person_participant(session, model, id_):
    stmt = await session.execute(
        select(model).where(
            model.owner == id_,
        )
    )
    result = stmt.scalars().first()
    return result


async def all_true(session, id_):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.community == id_,
                PersonParticipant.permission,
                true(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def all_false(session, id_):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.community == id_,
                PersonParticipant.permission == false(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def stop_double(session, model, obj, id_):
    stmt_admin = await session.execute(
        select(model)
        .where(
            model.community == id_,
            model.owner == obj,
        )
    )
    result = stmt_admin.scalars().first()
    return result
