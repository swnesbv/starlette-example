import shutil

from sqlalchemy import text
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from item.models import Item, Rent, ScheduleRent

from make_an_appointment.models import ReserveRentFor


async def period_item(start, end, session):
    # ..
    stmt = await session.execute(
        select(Item.id)
        .join(ReserveRentFor.rrf_item)
        .where(text(
            f"NOT daterange('{start}','{end}','[]') @> ANY(rsv_rrf.occupied) OR rsv_rrf.occupied IS NULL")
        )
    )
    result = stmt.scalars().all()
    # ..
    stmt = await session.execute(
        select(Item)
        .join(ScheduleRent.sch_r_item)
        .options(
            joinedload(Item.item_sch_r)
        )
        .where(Item.id.in_(result))
        .where(ScheduleRent.start < start)
        .where(ScheduleRent.end > end)
    )
    result = stmt.scalars().unique()
    # ..
    return result

async def not_period_item(session):
    # ..
    stmt = await session.execute(
        select(Item.id)
        .join(ReserveRentFor.rrf_item)
    )
    result = stmt.scalars().all()
    # ..
    stmt = await session.execute(
        select(Item)
        .join(ScheduleRent.sch_r_item)
        .options(joinedload(Item.item_sch_r))
        .where(Item.id.not_in(result))
    )
    result = stmt.scalars().unique()
    # ..
    return result


async def period_rent(start, end, session):
    # ..
    stmt = await session.execute(
        select(Rent.id)
        .join(ReserveRentFor.rrf_rent)
        .where(text(
            f"NOT daterange('{start}','{end}','[]') @> ANY(rsv_rrf.occupied) OR rsv_rrf.occupied IS NULL")
        )
    )
    result = stmt.scalars().all()
    # ..
    stmt = await session.execute(
        select(Rent)
        .join(
            ScheduleRent.sch_r_rent,
        )
        .options(
            joinedload(Rent.rent_sch_r,)
        )
        .where(Rent.id.in_(result))
        .where(ScheduleRent.start < start)
        .where(ScheduleRent.end > end)
    )
    result = stmt.scalars().unique()
    # ..
    return result

async def not_period_rent(session, id):
    # ..
    stmt = await session.execute(
        select(Rent.id)
        .join(ReserveRentFor.rrf_rent)
    )
    result = stmt.scalars().all()
    # ..
    stmt = await session.execute(
        select(Rent)
        .join(ScheduleRent.sch_r_rent)
        .options(joinedload(Rent.rent_sch_r))
        .where(Rent.id.not_in(result))
        .where(Rent.rent_belongs == id)
    )
    result = stmt.scalars().unique()
    # ..
    return result
