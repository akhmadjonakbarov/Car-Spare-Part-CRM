from sqladmin import ModelView
from .models import Purchase


class PurchaseAdmin(ModelView, model=Purchase):
    column_list = [
        Purchase.id,
        Purchase.user_id,
        Purchase.customer_id,
        Purchase.is_debt,
        Purchase.total_price,
        Purchase.remain_money,
        Purchase.paid_money,
    ]
    column_searchable_list = [Purchase.id]
    name = "Purchase"
    icon = "fa-solid fa-shopping-cart"
