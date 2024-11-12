
from starlette.routing import Route

from sitemap import sitemap


routes = [
    Route(
        "/sitemap",
        sitemap.all_sitemap,
        methods=["GET"]
    ),
]
