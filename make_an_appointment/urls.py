
from starlette.routing import Route

from . import rent, service


routes = [
    Route("/", rent.reserve_add, methods=["GET", "POST"]),
    Route("/choice-item", rent.reserve_choice_item, methods=["GET", "POST"]),
    Route("/choice-rent/{id:int}", rent.reserve_choice_rent, methods=["GET", "POST"]),
    Route("/list-rent", rent.reserve_list_rent),
    Route("/detail-rent/{id:int}", rent.reserve_detail_rent),
    Route("/update-rent/{id:int}", rent.reserve_update_rent, methods=["GET", "POST"]),
    Route("/delete-rrf/{id:int}", rent.rrf_delete, methods=["GET", "POST"]),
    # ..
    Route("/list-service", service.reserve_list_service),
    Route(
        "/rsv-service/{service:int}/{id:int}",
        service.create_reserve_service,
        methods=["GET", "POST"],
    ),
    Route("/detail-service/{id:int}", service.reserve_detail_service),
    Route(
        "/update-service/{id:int}",
        service.reserve_update_service,
        methods=["GET", "POST"],
    ),
    Route("/delete-rsf/{id:int}", service.delete, methods=["GET", "POST"]),
]
