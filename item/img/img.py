from datetime import datetime
import os
import shutil
from pathlib import Path, PurePosixPath

from PIL import Image

from starlette.exceptions import HTTPException

from config.settings import BASE_DIR

from auth_privileged.opt_slc import get_privileged_user


async def img_creat(file, mdl, email, id_fle, basewidth):
    # ..
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{mdl}/{email}/{id_fle}"
    # ..
    ext = PurePosixPath(file.filename).suffix
    file_path = f"{save_path}/{name}{ext}"
    # ..
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=400,
            detail="Format files: png, jpg, jpeg ..!",
        )
    if Path(file_path).exists():
        raise HTTPException(status_code=400, detail="Error..! File exists..!")
    os.makedirs(save_path, exist_ok=True)

    with open(file_path, "wb") as fle:
        fle.write(file.file.read())

        img = Image.open(file_path)
        # ..
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        # ..
        img_resize = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
        img_resize.save(file_path)

    return file_path.replace(".", "", 1)


async def sl_img_creat(
    request, session, file, mdl, id_sl, basewidth
):
    # ..
    prv = await get_privileged_user(request, session)
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{mdl}/{prv}/{id_sl}"
    # ..
    ext = PurePosixPath(file.filename).suffix
    file_path = f"{save_path}/{name}{ext}"
    #..
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=400,
            detail="Format files: png, jpg, jpeg ..!",
        )
    if Path(file_path).exists():
        raise HTTPException(
            status_code=400,
            detail="Error..! File exists..!"
        )

    os.makedirs(save_path, exist_ok=True)

    with open(file_path, "wb") as fle:
        fle.write(file.file.read())

        img = Image.open(file_path)
        # ..
        wpercent = basewidth/float(img.size[0])
        hsize = int((float(img.size[1])*float(wpercent)))
        # ..
        img_resize = img.resize((basewidth,hsize), Image.Resampling.LANCZOS)
        img_resize.save(file_path)

    return file_path.replace(".", "", 1)


# ..


async def item_img(name, save_path, file, basewidth):
    # ..
    ext = PurePosixPath(file.filename).suffix
    file_path = f"{save_path}/{name}{ext}"
    # ..
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=400,
            detail="Format files: png, jpg, jpeg ..!",
        )
    if Path(file_path).exists():
        raise HTTPException(status_code=400, detail="Error..! File exists..!")
    os.makedirs(save_path, exist_ok=True)

    with open(file_path, "wb") as fle:
        fle.write(file.file.read())

        img = Image.open(file_path)
        # ..
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        # ..
        img_resize = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
        img_resize.save(file_path)

    return file_path.replace(".", "", 1)


async def user_img_creat(file, email, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/user/{email}"
    obj = await item_img(name, save_path, file, basewidth)
    return obj

async def item_img_creat(file, email, id_, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{ email }/item/{ id_ }_tm"
    obj = await item_img(name, save_path, file, basewidth)
    return obj


async def rent_img_creat(file, email, tm_id, id_, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{ email }/item/{ tm_id }_tm/rent/{ id_ }"
    obj = await item_img(name, save_path, file, basewidth)
    return obj


async def service_img_creat(file, email, tm_id, id_, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{ email }/item/{ tm_id }_tm/service/{ id_ }"
    obj = await item_img(name, save_path, file, basewidth)
    return obj


async def del_user(email):
    # ..
    directory = [
        (BASE_DIR / f"static/upload/user/{email}"),
        (BASE_DIR / f"static/upload/{email}"),
    ]
    for i in directory:
        if Path(i).exists():
            shutil.rmtree(i)


async def del_tm(email, id_):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{ email }/item/{ id_ }_tm"
    )
    if Path(directory).exists():
        shutil.rmtree(directory)


async def del_rent(email, tm_id, id_):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{ email }/item/{ tm_id }_tm/rent/{ id_ }"
    )
    if Path(directory).exists():
        shutil.rmtree(directory)


async def del_service(email, tm_id, id_):
    # ..
    directory = (
        BASE_DIR
        / f"static/upload/{ email }/item/{ tm_id }_tm/service/{ id_ }"
    )
    if Path(directory).exists():
        shutil.rmtree(directory)
