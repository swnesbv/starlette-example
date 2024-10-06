from datetime import date, datetime, timedelta

import json

from sqlalchemy import insert, update as sqlalchemy_update, delete

from starlette import status
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from auth_privileged.opt_slc import get_privileged_user
from options_select.opt_slc import (
    id_and_owner,
    owner_request,
)
from .opt_slc import (
    period_item,
    period_rent,
    not_period_item,
    not_period_rent,
)

from .models import ReserveRentFor

templates = Jinja2Templates(directory="templates")


async def reserve_add(request):
    # ..
    template = "make_an_appointment/index.html"
    # ..
    if request.method == "GET":
        return templates.TemplateResponse(template, {"request": request})
    # ...
    if request.method == "POST":
        # ..
        form = await request.form()
        end = form["time_end"]
        start = form["time_start"]
        # ..
        if start >= end or start < date.today().strftime(settings.DATE):
            return PlainTextResponse("please enter proper dates")
        # ..
        payload = {
            "start": start,
            "end": end,
        }
        reserve = json.dumps(payload)
        # ..
        response = RedirectResponse(
            "/reserve/choice-item",
            status_code=302,
        )
        response.set_cookie("reserve", reserve)
        return response
# ..

async def get_token_reserve(request):
    if not request.cookies.get("reserve"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="not reserve token ..!",
        )
    token_get = request.cookies.get("reserve")
    token_loads = json.loads(token_get)
    return token_loads


# ..ITEM

# ...
async def reserve_choice_item(request):
    # ..
    token = await get_token_reserve(request)
    start = token["start"]
    end = token["end"]
    # ..
    time_start = datetime.strptime(start, settings.DATE)
    time_end = datetime.strptime(end, settings.DATE)
    # ..
    # rsv_period = []
    # for period in reserve_period:
    #     rsv_period.append(period.strftime(settings.DATE))
    rsv_period = await period_reserve(time_start, time_end)
    # ..
    template = "make_an_appointment/choice_item.html"

    async with async_session() as session:
        if request.method == "GET":
            if token:
                obj_list = await period_item(time_start, time_end, session)
                not_list = await not_period_item(session)

                context = {
                    "request": request,
                    "time_start": time_start,
                    "time_end": time_end,
                    "reserve_period": rsv_period,
                    "obj_list": obj_list,
                    "not_list": not_list,
                }

                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your token..!")
    await engine.dispose()


# ..RENT

# ...
async def reserve_choice_rent(request):
    # ..
    token = await get_token_reserve(request)
    start = token["start"]
    end = token["end"]
    # ..
    time_start = datetime.strptime(start, settings.DATE)
    time_end = datetime.strptime(end, settings.DATE)
    # ..
    rsv_period = await period_reserve(time_start, time_end)
    # ..
    id = request.path_params["id"]
    template = "make_an_appointment/choice_rent.html"

    async with async_session() as session:
        if request.method == "GET":
            if token:
                obj_list = await period_rent(time_start, time_end, session)
                not_list = await not_period_rent(session, id)
                context = {
                    "request": request,
                    "time_start": time_start,
                    "time_end": time_end,
                    "reserve_period": rsv_period,
                    "obj_list": obj_list,
                    "not_list": not_list,
                }

                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your token..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            rrf_rent_id = form["rrf_rent_id"]
            rrf_sch_r_id = form["rrf_sch_r_id"]
            # ..
            prv = await get_privileged_user(request, session)
            # ..
            if prv:
                if prv.id is not None:
                    query = insert(ReserveRentFor).values(
                        occupied=[time_start, time_end],
                        owner=prv.id,
                        rrf_item_id=id,
                        rrf_rent_id=int(rrf_rent_id),
                        rrf_sch_r_id=int(rrf_sch_r_id),
                        created_at=datetime.now(),
                    )
                    await session.execute(query)
                    await session.commit()
                    response = RedirectResponse(
                        f"/item/rent/details/{ rrf_rent_id }",
                        status_code=302,
                    )
                    return response
            query = insert(ReserveRentFor).values(
                occupied=[time_start, time_end],
                owner=request.user.user_id,
                rrf_item_id=id,
                rrf_rent_id=int(rrf_rent_id),
                rrf_sch_r_id=int(rrf_sch_r_id),
                created_at=datetime.now(),
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/item/rent/details/{ rrf_rent_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


# ...
async def reserve_list_rent(request):
    # ..
    template = "make_an_appointment/list_rent.html"

    async with async_session() as session:
        # ..
        prv = await get_privileged_user(request, session)
        if prv:
            if prv.id is not None:
                obj_list = await owner_request(session, ReserveRentFor, request.user.user_id)
                # ..
                if obj_list:
                    context = {
                        "request": request,
                        "obj_list": obj_list,
                    }
                    return templates.TemplateResponse(template, context)
            return PlainTextResponse(
                "either it's not your account or you don't have a reservation.!"
            )
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="not token privileged..!",
        )


# ...
async def reserve_detail_rent(request):
    # ..
    id = request.path_params["id"]
    template = "make_an_appointment/details_rent.html"

    async with async_session() as session:
        # ..
        i = await id_and_owner(session, ReserveRentFor, request.user.user_id, id)
        if i:
            context = {
                "request": request,
                "i": i,
            }
            return templates.TemplateResponse(template, context)
        return PlainTextResponse(
            "either it's not your account, or you don't have one. booking positions..!"
        )
    await engine.dispose()


# ...
async def reserve_update_rent(request):
    # ..
    id = request.path_params["id"]
    template = "/make_an_appointment/update_rent.html"

    async with async_session() as session:
        # ..
        i = await id_and_owner(session, ReserveRentFor, request.user.user_id, id)
        # ..
        rsv_period = await period_reserve(i.time_start, i.time_end)
        # ..
        context = {"request": request, "i": i, "rsv_period": rsv_period}
        # ...
        if request.method == "GET":
            if i:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            form = await request.form()
            # ..
            end = form["time_end"]
            start = form["time_start"]
            description = form["description"]
            # ..
            time_end = datetime.strptime(end, settings.DATE)
            time_start = datetime.strptime(start, settings.DATE)
            # ..
            if start >= end or start < date.today().strftime(settings.DATE):
                return PlainTextResponse("please enter proper dates")
            # ..
            query = (
                sqlalchemy_update(ReserveRentFor)
                .where(ReserveRentFor.id == id)
                .values(
                    occupied=[time_start, time_end],
                    description=description,
                    modified_at=datetime.now(),
                )
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()

            response = RedirectResponse(
                f"/reserve/detail-rent/{ i.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


# ...
async def rrf_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/make_an_appointment/delete.html"

    async with async_session() as session:
        # ...
        if request.method == "GET":
            # ..
            i = await id_and_owner(session, ReserveRentFor, request.user.user_id, id)
            if i:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "i": i,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(ReserveRentFor).where(ReserveRentFor.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()



async def period_reserve(time_start, time_end):
    reserve_period = [
        time_start + timedelta(days=x)
        for x in range(0, (time_end - time_start).days + 1)
    ]
    rsv_period = [i.strftime(settings.DATE) for i in reserve_period]
    # ..
    rsv_period = str(rsv_period).replace("'", "").replace("[", "").replace("]", "")
    return rsv_period
