
from datetime import datetime

from .img import item_img


async def im_creat(file, email, tm_id, id_, basewidth):
    name = datetime.now().strftime("%d-%m-%y-%H-%M")
    save_path = f"./static/upload/{ email }/item/{tm_id}_tm/service/{ id_ }"
    obj = await item_img(name, save_path, file, basewidth)
    return obj
