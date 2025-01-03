from __future__ import annotations

from datetime import datetime, date, timedelta

import json, string, secrets, time

from passlib.hash import pbkdf2_sha1

from account.models import User
from auth_privileged.models import Privileged

from comment.models import Comment

from collocutor.models import PersonCollocutor
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageGroup, OneOneChat
from item.models import (
    Item,
    Rent,
    Service,
    ScheduleService,
    ScheduleRent,
    DumpService,
    Slider,
)
from make_an_appointment.models import ReserveRentFor, ReserveServicerFor

from db_config.storage_config import Base, engine, async_session


def get_random_string():
    alphabet = string.ascii_letters + string.digits
    prv_key = "".join(secrets.choice(alphabet) for i in range(32))
    return prv_key


async def on_app_startup() -> None:
    async with engine.begin() as conn:
        # ..
        start = time.time()
        print(" start..")
        # ..
        await conn.run_sync(Base.metadata.create_all)
        # ..
        end = time.time()
        print(" end..", end - start)

    async with async_session() as session:
        async with session.begin():
            # ..
            password_hash = pbkdf2_sha1.hash("password")
            # ..
            start = time.time()
            print(" start add_all..")
            # ..
            session.add_all(
                [
                    User(
                        name="one",
                        email="one@example.com",
                        password=password_hash,
                        is_admin=True,
                        is_active=True,
                        privileged=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    User(
                        name="two",
                        email="two@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        privileged=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    User(
                        name="three",
                        email="three@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    User(
                        name="four",
                        email="four@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    Privileged(
                        prv_key=get_random_string(),
                        prv_in=1,
                    ),
                    GroupChat(
                        title="chat group (one)",
                        description="description group (one) owner: one@example.com",
                        owner=1,
                        created_at=datetime.now(),
                    ),
                    MessageGroup(
                        message="message",
                        owner=1,
                        id_group=1,
                        created_at=datetime.now(),
                    ),
                    PersonParticipant(
                        explanatory_note="gr-1 admin - note",
                        permission=1,
                        owner=1,
                        community=1,
                        created_at=datetime.now(),
                    ),
                    PersonParticipant(
                        explanatory_note="gr-1 three - note",
                        permission=0,
                        owner=3,
                        community=1,
                        created_at=datetime.now(),
                    ),
                    PersonCollocutor(
                        ref_num="1-2",
                        explanatory_note="note..1+2",
                        permission=1,
                        owner=1,
                        community=2,
                        created_at=datetime.now(),
                    ),
                    PersonCollocutor(
                        explanatory_note="note..2+3",
                        permission=0,
                        owner=2,
                        community=3,
                        created_at=datetime.now(),
                    ),
                    PersonCollocutor(
                        explanatory_note="note..4+3",
                        permission=0,
                        owner=4,
                        community=3,
                        created_at=datetime.now(),
                    ),
                    OneOneChat(
                        message="OneOneChat message",
                        owner=1,
                        one_one=1,
                        created_at=datetime.now(),
                    ),
                    Item(
                        title="item 01 one",
                        description="description",
                        categories=["cat_1"],
                        owner=1,
                        created_at=datetime.now(),
                    ),
                    Item(
                        title="item 02 two",
                        description="description 02 two",
                        categories=["cat_1", "cat_2"],
                        owner=2,
                        created_at=datetime.now(),
                    ),
                    Item(
                        title="item 03 three",
                        description="description 03 two",
                        categories=["cat_1", "cat_2", "cat_3"],
                        owner=3,
                        created_at=datetime.now(),
                    ),
                    Item(
                        title="item 04 four",
                        description="description 03 two",
                        categories=["cat_2", "cat_3"],
                        owner=4,
                        created_at=datetime.now(),
                    ),
                    Rent(
                        title="rent 01 to it 1",
                        description="description.. rent 01",
                        owner=1,
                        rent_belongs=1,
                        created_at=datetime.now(),
                    ),
                    Rent(
                        title="rent 02 to it 1",
                        description="description.. rent 02",
                        owner=1,
                        rent_belongs=1,
                        created_at=datetime.now(),
                    ),
                    Rent(
                        title="rent 03 to it 2",
                        description="description.. rent 03",
                        owner=1,
                        rent_belongs=2,
                        created_at=datetime.now(),
                    ),
                    Service(
                        title="service 01",
                        description="description 01",
                        owner=1,
                        service_belongs=1,
                        created_at=datetime.now(),
                    ),
                    Comment(
                        opinion="01 (one) item-opinion description",
                        user_on={"name": "one", "email": "one@example.com"},
                        owner=1,
                        cmt_item_id=1,
                        created_at=datetime.now(),
                    ),
                    Comment(
                        opinion="01 (one) service-opinion description",
                        user_on={"name": "one", "email": "one@example.com"},
                        owner=1,
                        cmt_service_id=1,
                        created_at=datetime.now(),
                    ),
                    Comment(
                        opinion="01 (one) rent-opinion description",
                        user_on={"name": "two", "email": "two@example.com"},
                        owner=2,
                        cmt_rent_id=1,
                        created_at=datetime.now(),
                    ),
                    ScheduleRent(
                        title="rent 01 ScheduleRent 01",
                        description="description.. rent 01 ScheduleRent 01",
                        owner=1,
                        sch_r_item_id=1,
                        sch_r_rent_id=1,
                        created_at=datetime.now(),
                    ),
                    ScheduleService(
                        name="name 01 Service 01",
                        title="service 01 ScheduleService 01",
                        description="description.. id-1 service 01 ScheduleService 01",
                        type_on="event",
                        number_on=date.today(),
                        there_is=datetime.now(),
                        owner=1,
                        sch_s_item_id=1,
                        sch_s_service_id=1,
                        created_at=datetime.now(),
                    ),
                    ScheduleService(
                        name="name 02 Service 01",
                        title="service 01 ScheduleService 02",
                        description="description.. id-2 service 01 ScheduleService 02",
                        type_on="birthday",
                        number_on=date.today(),
                        there_is=datetime.now() + timedelta(minutes=60),
                        owner=1,
                        sch_s_item_id=1,
                        sch_s_service_id=1,
                        created_at=datetime.now(),
                    ),
                    ReserveRentFor(
                        # time_start=date.today(),
                        # time_end=date.today() + timedelta(days=1),
                        owner=1,
                        rrf_item_id=1,
                        rrf_rent_id=1,
                        rrf_sch_r_id=1,
                        created_at=datetime.now(),
                    ),
                    ReserveRentFor(
                        # time_start=date.today() + timedelta(days=3),
                        # time_end=date.today() + timedelta(days=4),
                        owner=1,
                        rrf_item_id=1,
                        rrf_rent_id=1,
                        rrf_sch_r_id=1,
                        created_at=datetime.now(),
                    ),
                    ReserveServicerFor(
                        reserve_time=datetime.now(),
                        owner=1,
                        rsf_service_id=1,
                        rsf_sch_s_id=1,
                        created_at=datetime.now(),
                    ),
                    DumpService(
                        title=datetime.now(),
                        owner=1,
                        dump_s_service_id=1,
                    ),
                    Slider(id=1,),
                ]
            )
            await session.flush()
        await session.commit()
        end = time.time()
        print(" end add_all..", end - start)
    await engine.dispose()


async def on_app_shutdown() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
