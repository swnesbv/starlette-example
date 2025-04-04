
from starlette.routing import Route

from . import (
    item,
    rent,
    service,
    schedule_rent,
    schedule_service,
    schedule_export_csv,
    schedule_import_csv,

)


routes = [
    Route(
        "/dump_{id:int}",
        schedule_export_csv.export_csv,
        methods=["GET"],
    ),
    #..
    Route(
        "/dump-csv/{id:int}",
        schedule_export_csv.dump_csv,
        methods=["GET"],
    ),
    Route(
        "/dump/{id:int}",
        schedule_export_csv.delete_user_csv,
        methods=["GET", "POST"],
    ),

    #...
    Route(
        "/import-csv/{id:int}",
        schedule_import_csv.import_sch_csv,
        methods=["GET", "POST"],
    ),
    Route("/item-import-csv", item.import_item_csv, methods=["GET", "POST"]),
    # ...

    Route(
        "/item-export-csv",
        item.export_item_csv,
        methods=["GET"],
    ),
    # ..
    Route("/search", item.search, methods=["GET", "POST"]),
    # ..
    Route("/list", item.item_list),
    Route("/item/details/{id:int}", item.item_details),

    Route("/item/categories/{cts:str}", item.item_categories, methods=["GET", "POST"]),

    Route("/create", item.item_create, methods=["GET", "POST"]),
    Route("/update/{id:int}", item.item_update, methods=["GET", "POST"]),
    Route("/delete/{id:int}", item.item_delete, methods=["GET", "POST"]),
    # ..
    Route("/rent/list", rent.rent_list),
    Route("/rent/list-prv", rent.rent_list_prv),
    Route("/rent/details/{id:int}", rent.rent_details),
    Route("/rent/create", rent.rent_create, methods=["GET", "POST"]),
    Route("/rent/update/{id:int}", rent.rent_update, methods=["GET", "POST"]),
    Route("/rent/delete/{id:int}", rent.rent_delete, methods=["GET", "POST"]),
    # ..
    Route("/service/list", service.service_list),
    Route("/service/details/{id:int}", service.service_details),
    Route("/service/create", service.service_create, methods=["GET", "POST"]),
    Route("/service/update/{id:int}", service.service_update, methods=["GET", "POST"]),
    Route("/service/delete/{id:int}", service.service_delete, methods=["GET", "POST"]),
    # ..
    Route("/schedulerent/list", schedule_rent.list_sch_rent),
    Route(
        "/schedulerent/details/{id:int}",
        schedule_rent.details_sch_rent,
        methods=["GET", "POST"],
    ),
    Route("/schedulerent/create/", schedule_rent.create_sch_rent, methods=["GET", "POST"]),
    Route(
        "/schedulerent/update/{id:int}",
        schedule_rent.update_sch_rent,
        methods=["GET", "POST"],
    ),
    Route(
        "/schedulerent/delete/{id:int}", schedule_rent.schedule_sch_delete, methods=["GET", "POST"]
    ),
    # ..
    Route("/scheduleservice/list-service", schedule_service.list_sch_service),
    Route("/scheduleservice/list/{id:int}", schedule_service.list_sch_service_id),
    # ...
    Route(
        "/scheduleservice/details/{service:int}/{id:int}",
        schedule_service.details_sch_service,
        methods=["GET", "POST"],
    ),
    Route(
        "/scheduleservice/details/{id:int}",
        schedule_service.details,
        methods=["GET", "POST"],
    ),
    # ...
    Route(
        "/scheduleservice/create",
        schedule_service.create_sch_service,
        methods=["GET", "POST"],
    ),
    Route(
        "/scheduleservice/update/{id:int}",
        schedule_service.update_sch_service,
        methods=["GET", "POST"],
    ),
    Route(
        "/scheduleservice/delete/{id:int}",
        schedule_service.schedule_sch_delete,
        methods=["GET", "POST"],
    ),
]
