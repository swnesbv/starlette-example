import subprocess
from starlette.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


async def all_sitemap(request):
    if request.method == "GET":

        subprocess.Popen(["./ENV/Scripts/python", "generate_sitemap.py"])

        template = "/sitemap.html"
        return templates.TemplateResponse(template, {"request": request})
