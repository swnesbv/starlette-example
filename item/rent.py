import json

from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from account.models import User

from options_select.opt_slc import (
    for_id,
    rent_comment,
)

from auth_privileged.opt_slc import privileged, id_and_owner_prv, token_privileged

from .create_update import child_img_create, child_img_update

from .img import im_rent, img
from .models import Item, Rent, ScheduleRent

templates = Jinja2Templates(directory="templates")


@privileged()
# ...
async def rent_create(request):
    # ..
    form = await request.form()
    belongs = form.get("belongs")
    new = Rent()
    # ..
    if belongs is not None:
        new.rent_belongs = int(belongs)
    # ..
    obj = await child_img_create(
        request, form, belongs, Item, new, "rent", "item", im_rent
    )
    return obj


@privileged()
# ...
async def rent_update(request):
    # ..
    id_ = request.path_params["id"]
    # ..
    obj = await child_img_update(
        request, Rent, id_, "service", im_rent
    )
    return obj


@privileged()
# ...
async def rent_delete(request):
    # ..
    id_ = request.path_params["id"]
    template = "/rent/delete.html"
    # ..
    async with async_session() as session:
        if request.method == "GET":
            # ..
            i = await id_and_owner_prv(request, session, Rent, id_)
            # ..
            if i:
                return templates.TemplateResponse(
                    template,
                    {"request": request},
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            i = await id_and_owner_prv(request, session, Rent, id_)
            email = await for_id(session, User, i.owner)
            # ..
            await img.del_rent(email.email, i.rent_belongs, id_)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/rent/list",
                status_code=302,
            )
            return response
    await engine.dispose()


async def rent_list(request):
    # ..
    template = "/rent/list.html"
    # ..
    async with async_session() as session:
        # ..
        stmt = await session.execute(select(Rent).order_by(Rent.created_at.desc()))
        obj_list = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def rent_list_prv(request):
    # ..
    template = "/rent/list_prv.html"
    # ..
    async with async_session() as session:
        # ..
        i = await token_privileged(request, session, Rent)
        if i:
            context = {
                "request": request,
                "obj_list": i,
            }
            return templates.TemplateResponse(template, context)
        return RedirectResponse("/privileged/login")
    await engine.dispose()


async def rent_details(request):
    # ..
    id_ = request.path_params["id"]
    template = "/rent/details.html"
    # ..
    async with async_session() as session:
        # ..
        cmt_list = await rent_comment(session, id_)
        # ..
        i = await for_id(session, Rent, id_)
        # ..
        stmt = await session.execute(
            select(ScheduleRent)
            .where(ScheduleRent.sch_r_rent_id == id_)
            .order_by(ScheduleRent.id.desc())
        )
        obj_list = stmt.scalars().all()
        # ..
        obj = [
            {
                "start": to.start,
                "end": to.end,
                "title": to.title,
            }
            for to in obj_list
        ]
        sch_json = json.dumps(obj, default=str)
        # ..
        context = {
            "request": request,
            "i": i,
            "cmt_list": cmt_list,
            "obj_list": obj_list,
            "sch_json": sch_json,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()
