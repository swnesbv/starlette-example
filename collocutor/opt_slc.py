import os, jwt, json, string, secrets, functools

from sqlalchemy import and_, true, false
from sqlalchemy.future import select

from account.models import User

from .models import PersonCollocutor


async def stop_double(session, obj):
    stmt = await session.execute(
        select(User.id)
        .join(
            PersonCollocutor.call_community,
        )
        .where(
            PersonCollocutor.owner == obj,
        )
    )
    result = stmt.scalars().all()
    stmt = await session.execute(
        select(User)
        .where(
            User.id.not_in(result),
        )
        .where(
            User.id != obj,
        )
    )
    obj_list = stmt.scalars().all()
    print(" type obj_list..", type(obj_list))
    return obj_list


async def owner_true(session, obj):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            and_(
                PersonCollocutor.owner == obj,
                PersonCollocutor.permission,
                true(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def owner_false(session, obj):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            and_(
                PersonCollocutor.owner == obj,
                PersonCollocutor.permission == false(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def to_user_true(session, obj):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            and_(
                PersonCollocutor.community == obj,
                PersonCollocutor.permission,
                true(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def to_user_false(session, obj):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            and_(
                PersonCollocutor.community == obj,
                PersonCollocutor.permission == false(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def person_collocutor(session, obj, id_):
    stmt = await session.execute(
        select(PersonCollocutor).where(
            and_(
                PersonCollocutor.id == id_,
                PersonCollocutor.community == obj
            )
        )
    )
    result = stmt.scalars().first()
    return result
