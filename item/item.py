import ast

from sqlalchemy.future import select

from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from db_config.storage_config import engine, async_session

from account.models import User

from options_select.opt_slc import (
    for_id,
    item_comment,
    id_and_owner,
)

from options_select.csv_import import import_csv
from options_select.csv_export import export_csv

from auth_privileged.opt_slc import (
    get_privileged_user,
    privileged,
)
from options_select.opt_slc import left_right_first

from .models import Item, Service, Rent

from .img import im_item, img
from .create_update import parent_create, child_img_update


templates = Jinja2Templates(directory="templates")


async def item_categories(request):
    # ..
    async with async_session() as session:
        # ..
        if request.method == "GET":
            # ..
            template = "/item/categories.html"
            categories = request.path_params["cts"]
            # ..
            a = categories.replace("%20", " ")
            output = ast.literal_eval(a)
            # ..
            stmt = await session.execute(
                select(Item)
                .where(
                    Item.categories.contains(output)
                )
            )
            obj_list = stmt.scalars().all()
            # ..
            stmt = await session.execute(
                select(Item.categories)
            )
            output = stmt.scalars().all()

            obj = []
            for x in output:
                if x is not None:
                    obj.extend(x)

            _ = list(set(obj))

            obj_unique = []
            # for x in obj:
            #     if x not in obj_unique:
            #         obj_unique.append(x)
            _ = [obj_unique.append(x) for x in obj if x not in obj_unique]

            # ..
            context = {
                "request": request,
                "obj_list": obj_list,
                "obj_unique": obj_unique,
            }
            # ..
            return templates.TemplateResponse(template, context)

    if request.method == "POST":
        form = await request.form()
        on_off = form.getlist("on_off")
        cts = form.getlist("categories")

        params = []
        for (c, d) in zip(on_off, cts):
            if c == "1" :
                params.append(d)
        print(" params..", params)
        print("..")
        return RedirectResponse(
            f"/item/item/categories/{params}",
            status_code=302,
        )


@privileged()
# ...
async def export_item_csv(request):
    async with async_session() as session:
        # ..
        if request.method == "GET":
            # ..
            obj = await export_csv(request, session)
            # ..
            return obj
            # ..
    await engine.dispose()


@privileged()
# ...
async def import_item_csv(request):
    # ..
    template = "/item/item_import_csv.html"
    # ..
    async with async_session() as session:
        # ..
        if request.method == "GET":
            return templates.TemplateResponse(
                template,
                {
                    "request": request,
                },
            )
        # ...
        if request.method == "POST":
            # ..
            prv = await get_privileged_user(request, session)
            # ..
            await import_csv(request, session, Item, prv)
            await session.commit()
            # ..
            return RedirectResponse(
                "/item/list",
                status_code=302,
            )

    await engine.dispose()


@privileged()
# ...
async def item_create(request):
    if request.method == "GET":
        async with async_session() as session:
            prv = await get_privileged_user(request, session)
            owner_exist = await left_right_first(session, Item, Item.owner, prv.id)
            if owner_exist:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=" owner already registered..!",
                )
    obj = await parent_create(request, Item, "item", im_item)
    return obj


@privileged()
# ...
async def item_update(request):
    # ..
    id_ = request.path_params["id"]
    obj = await child_img_update(request, Item, id_, "item", im_item)
    return obj


@privileged()
# ...
async def item_delete(request):
    # ..
    id_ = request.path_params["id"]
    template = "/item/delete.html"

    async with async_session() as session:
        if request.method == "GET":
            # ..
            prv = await get_privileged_user(request, session)
            # ..
            i = await id_and_owner(session, Item, prv.id, id_)
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
            prv = await get_privileged_user(request, session)
            # ..
            i = await id_and_owner(
                session, Item, prv.id, id_
            )
            email = await for_id(session, User, i.owner)
            # ..
            await img.del_tm(email.email, i.id)
            # ..
            await session.delete(i)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/item/list",
                status_code=302,
            )
            return response
    await engine.dispose()


async def item_list(request):
    # ..
    template = "/item/list.html"

    async with async_session() as session:
        # ..
        stmt = await session.execute(
            select(Item).order_by(Item.created_at.desc())
        )
        obj_list = stmt.scalars().all()
        # ..
        context = {
            "request": request,
            "obj_list": obj_list,
        }
        return templates.TemplateResponse(template, context)
    await engine.dispose()


async def item_details(request):
    # ..
    id_ = request.path_params["id"]
    template = "/item/details.html"
    # ..
    async with async_session() as session:
        # ..
        i = await for_id(session, Item, id_)
        cmt_list = await item_comment(session, id_)
        prv = await get_privileged_user(request, session)
        # ..
        if i:
            stmt = await session.execute(
                select(Rent).where(Rent.rent_belongs == id_)
            )
            all_rent = stmt.scalars().all()
            # ..
            stmt = await session.execute(
                select(Service).where(Service.service_belongs == id_)
            )
            all_service = stmt.scalars().all()
            # ..
            context = {
                "request": request,
                "i": i,
                "prv": prv,
                "cmt_list": cmt_list,
                "all_rent": all_rent,
                "all_service": all_service,
            }
            # ..
            return templates.TemplateResponse(template, context)
        return RedirectResponse("/item/list", status_code=302)
    await engine.dispose()


async def search(request):
    # ..
    query = request.query_params.get("query")
    template = "/item/search.html"
    # ..
    async with async_session() as session:
        if request.method == "GET":
            # ..
            stmt = await session.execute(
                select(Item).where(Item.title.like("%" + query + "%"))
            )
            search_title = stmt.scalars().all()
            # ...
            context = {
                "request": request,
                "search_title": search_title,
            }
            # ..
            return templates.TemplateResponse(template, context)
    await engine.dispose()
