from fastapi import FastAPI
from sqladmin import Admin
from starlette.staticfiles import StaticFiles

from apps.routes import main_router
from config.settings import settings
from fastapi_pagination import add_pagination
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config.dashboard_security import authentication_backend
from config.database_config import engine
from apps.routes import main_router
from sqladmin import Admin

from apps.product_manager.admin import (
    ItemAdmin,
    CategoryAdmin,
    UnitAdmin,
    TypeAdmin,
    TypeItemAdmin,
    CarAdmin,
)
from apps.user.admin import UserAdmin
from apps.customer.admin import CustomerAdmin, PaymentHistoryAdmin
from apps.role_manager.admin import RoleAdmin, SalaryTypeAdmin, EmployeeAdmin
from apps.transaction.admin import TransactionAdmin
from apps.purchase.admin import PurchaseAdmin
from apps.document.admin import (
    DocumentAdmin,
    DocumentItemAdmin,
    DocumentItemBalanceAdmin,
)
from apps.permissions.admin import PermissionAdmin
from apps.action.admin import ActionAdmin
from apps.currency.admin import CurrencyAdmin

from apps.initializer.admin import InitializerAdmin
from apps.notes.admin import NoteAdmin

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
)


@app.on_event("startup")
async def on_startup():
    from apps.base.models import Base
    from config.database_config import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


admin = Admin(
    app,
    engine,
    base_url="/admin",
    authentication_backend=authentication_backend,
)

admin.add_view(UserAdmin)
admin.add_view(CustomerAdmin)
admin.add_view(PaymentHistoryAdmin)
admin.add_view(RoleAdmin)
admin.add_view(SalaryTypeAdmin)
admin.add_view(EmployeeAdmin)
admin.add_view(TransactionAdmin)
admin.add_view(PurchaseAdmin)
admin.add_view(DocumentAdmin)
admin.add_view(DocumentItemAdmin)
admin.add_view(DocumentItemBalanceAdmin)
admin.add_view(PermissionAdmin)
admin.add_view(ActionAdmin)
admin.add_view(CurrencyAdmin)
admin.add_view(ItemAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(UnitAdmin)
admin.add_view(TypeAdmin)
admin.add_view(TypeItemAdmin)
admin.add_view(CarAdmin)
admin.add_view(InitializerAdmin)
admin.add_view(NoteAdmin)

app.mount(
    "/statistics", StaticFiles(directory="ds_files/statistics"), name="statistics"
)
app.include_router(main_router)

add_pagination(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
