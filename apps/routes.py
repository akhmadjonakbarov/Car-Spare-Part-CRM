from fastapi import APIRouter

from apps.currency import routes as currency_routes
from apps.product_manager.routes import (
    product_routes,
    unit_routes,
    category_routes,
    document_routes,
    store_routes,
    doc_item_routes,
    type_routes,
    car_routes,
)
from apps.permissions import routes as permissions_routes
from apps.action import routes as action_routes
from apps.notes import routes as notes_routes
from apps.statistics import routes as statistics_routes
from apps.user import routes as user_routes
from apps.purchase import routes as purchase_routes
from apps.customer import routes as customer_routes
from apps.transaction import routes as transaction_routes
from apps.company import routes as company_routes
from config.settings import settings

main_router = APIRouter(
    prefix=settings.API_V1,
)

main_router.include_router(user_routes.router)
main_router.include_router(action_routes.router)
main_router.include_router(permissions_routes.router)
main_router.include_router(customer_routes.router)
main_router.include_router(transaction_routes.router)
main_router.include_router(document_routes.router)
main_router.include_router(doc_item_routes.router)
main_router.include_router(store_routes.router)
main_router.include_router(category_routes.router)
main_router.include_router(unit_routes.router)
main_router.include_router(type_routes.router)
main_router.include_router(product_routes.router)
main_router.include_router(purchase_routes.router)
main_router.include_router(currency_routes.router)
main_router.include_router(statistics_routes.router)
main_router.include_router(notes_routes.router)
main_router.include_router(car_routes.router)
main_router.include_router(company_routes.router)
