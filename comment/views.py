from datetime import datetime

from sqlalchemy import update as sqlalchemy_update, delete
from sqlalchemy.future import select

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

# from mail.send import send_mail
from account.models import User
from account.opt_slc import auth

from db_config.storage_config import engine, async_session

from auth_privileged.opt_slc import get_privileged_user
from options_select.opt_slc import for_id, id_and_owner

from .models import Comment


templates = Jinja2Templates(directory="templates")


# ..CREATE
async def cmt_child_create(request, new, id_, item):
    # ..
    template = "/comment/create.html"

    async with async_session() as session:
        # ..
        owner = int()
        if request.cookies.get("visited"):
            owner = request.user.user_id
        if request.cookies.get("privileged"):
            obj = await get_privileged_user(request, session)
            owner = int(obj.id)
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
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            new.opinion = opinion
            new.owner = owner
            new.created_at = datetime.now()
            # ..
            session.add(new)
            await session.flush()
            i = await for_id(session, User, new.owner)
            new.user_on = {"name": i.name, "email": i.email}
            session.add(new)
            await session.commit()
            # ..
            # await send_mail(
            #     f"A new object has been created - {owner} - { id_ }: {opinion}"
            # )
            # ..
            response = RedirectResponse(
                f"/item/{item}/details/{ id_ }",
                status_code=302,
            )
            return response
    await engine.dispose()


@auth()
# ...
async def cmt_item_create(request):
    # ..
    id_ = request.path_params["id"]
    # ..
    new = Comment()
    new.cmt_item_id = id_
    # ..
    obj = await cmt_child_create(
        request, new, id_, "item"
    )
    return obj


@auth()
# ...
async def cmt_rent_create(request):
    # ..
    id_ = request.path_params["id"]
    # ..
    new = Comment()
    new.cmt_rent_id = id_
    # ..
    obj = await cmt_child_create(
        request, new, id_, "item"
    )
    return obj


@auth()
# ...
async def cmt_service_create(request):
    # ..
    id_ = request.path_params["id"]
    # ..
    new = Comment()
    new.cmt_service_id = id_
    # ..
    obj = await cmt_child_create(
        request, new, id_, "item"
    )
    return obj


async def in_comment(request, session, id_):
    # ..
    if request.cookies.get("visited"):
        stmt = await session.execute(
            select(Comment)
            .where(Comment.id == id_)
            .where(Comment.owner == request.user.user_id)
        )
        result = stmt.scalars().first()
        return result
    # ..
    if request.cookies.get("privileged"):
        obj = await get_privileged_user(request, session)
        owner = int(obj.id)
        stmt = await session.execute(
            select(Comment)
            .where(Comment.id == id_)
            .where(Comment.owner == owner)
        )
        result = stmt.scalars().first()
        return result


async def cmt_child_update(request, id_, cmt_i_id, item):
    # ..
    template = "/comment/update.html"
    # ..
    async with async_session() as session:
        # ..
        i = await in_comment(request, session, id_)
        # ..
        if request.method == "GET":
            if i:
                context = {
                    "request": request,
                    "i": i,
                }
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            opinion = form["opinion"]
            # ..
            query = (
                sqlalchemy_update(Comment)
                .where(Comment.id == id_)
                .values(opinion=opinion, modified_at=datetime.now())
                .execution_options(synchronize_session="fetch")
            )
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            # await send_mail(f"changes were made at the facility - {i}: {opinion}")
            # ..
            response = RedirectResponse(
                f"/item/{item}/details/{ cmt_i_id }",
                status_code=302,
            )
            return response
    await engine.dispose()


@auth()
# ...
async def cmt_item_update(request):
    # ..
    id_ = request.path_params["id"]
    # ..
    async with async_session() as session:
        i = await for_id(session, Comment, id_)
        obj = await cmt_child_update(
            request, id_, i.cmt_item_id, "item"
        )
        return obj
    await engine.dispose()


@auth()
# ...
async def cmt_rent_update(request):
    # ..
    id_ = request.path_params["id"]
    # ..
    async with async_session() as session:
        i = await for_id(session, Comment, id_)
        obj = await cmt_child_update(
            request, id_, i.cmt_rent_id, "rent"
        )
        return obj
    await engine.dispose()


@auth()
# ...
async def cmt_service_update(request):
    # ..
    id_ = request.path_params["id"]
    # ..
    async with async_session() as session:
        i = await for_id(session, Comment, id_)
        obj = await cmt_child_update(
            request, id_, i.cmt_service_id, "service"
        )
        return obj
    await engine.dispose()


# ...
async def cmt_delete(request):
    # ..
    id_ = request.path_params["id"]
    template = "/comment/delete.html"
    # ..
    async with async_session() as session:
        # ..
        if request.method == "GET":
            # ..
            detail = await id_and_owner(session, Comment, request.user.user_id, id_)
            # ..
            if detail:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "detail": detail,
                    },
                )
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(Comment).where(Comment.id == id_)
            # ..
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/",
                status_code=302,
            )
            return response
    await engine.dispose()
