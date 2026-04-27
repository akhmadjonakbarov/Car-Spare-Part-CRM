from sqladmin import ModelView
from .models import Transaction


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [
        Transaction.id,
        Transaction.customer_id,
        Transaction.amount,
        Transaction.purchase_id,
    ]
    name = "Transaction"
    icon = "fa-solid fa-exchange-alt"
