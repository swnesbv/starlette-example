from datetime import datetime

import json

from sqlalchemy import delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from json2html import json2html

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from auth_privileged.opt_slc import (
    privileged,
    get_owner_prv,
    id_and_owner_prv,
)

from .create_update import child_create, child_update
from .models import Rent, ScheduleRent

templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def create_sch_rent(request):
    context = {}
    # ..
    form = await request.form()
    start = form.get("start")
    end = form.get("end")
    s = form.get("sch_r_rent_id")
    # ..
    new = ScheduleRent()

    if start is not None and end is not None and s is not None:
        i = s.split(",")
        new.start = datetime.strptime(start, settings.DATE_T)
        new.end = datetime.strptime(end, settings.DATE_T)
        new.sch_r_item_id = int(i[1])
        new.sch_r_rent_id = int(i[0])
        new.start_end = [new.start, new.end]
    # ..
    obj = await child_create(
        request, context, form, Rent, new, "schedulerent", "rent"
    )
    return obj


@privileged()
# ...
async def update_sch_rent(request):
    # ..
    context = {}
    id_ = request.path_params["id"]
    # ..
    form = await request.form()
    # ..
    start = form.get("start")
    end = form.get("end")
    title = form.get("title")
    description = form.get("description")
    # ..
    if start and end is not None:
        form = {
        "start": datetime.strptime(start, settings.DATE_T),
        "end": datetime.strptime(end, settings.DATE_T),
        "title": title,
        "description": description,
        }
        # ..
    obj = await child_update(request, context, ScheduleRent, id_, form, "schedulerent")
    return obj


@privileged()
# ...
async def schedule_sch_delete(request):
    # ..
    id_ = request.path_params["id"]
    template = "/schedulerent/delete.html"
    # ..
    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner_prv(request, session, ScheduleRent, id_)
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
            query = delete(ScheduleRent).where(ScheduleRent.id == id_)
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/schedulerent/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@privileged()
# ...
async def list_sch_rent(request):
    # ..
    template = "/schedulerent/list.html"
    # ..
    async with async_session() as session:
        # ..
        obj_list = await get_owner_prv(request, session, ScheduleRent)
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


@privileged()
# ...
async def details_sch_rent(request):
    # ..
    context = {}
    id_ = request.path_params["id"]
    template = "/schedulerent/details.html"
    # ..
    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner_prv(request, session, ScheduleRent, id_)
            if i:
                # ..
                obj_list = await get_owner_prv(request, session, ScheduleRent)
                # ..
                obj = [
                    {
                        "id": to.id,
                        "title": to.title,
                        "start": to.start,
                        "end": to.end,
                    }
                    for to in obj_list
                ]
                sch_json = json.dumps(obj, default=str)
                table_attributes = "style='width:100%', class='table table-bordered'"
                sch_json = json2html.convert(
                    json=sch_json, table_attributes=table_attributes
                )
                context = {
                    "request": request,
                    "sch_json": sch_json,
                    "i": i,
                }
            return templates.TemplateResponse(template, context)
    await engine.dispose()
