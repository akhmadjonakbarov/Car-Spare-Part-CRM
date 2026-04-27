from sqladmin import ModelView
from .models import Customer, PaymentHistory


class CustomerAdmin(ModelView, model=Customer):
    column_list = [
        Customer.id,
        Customer.full_name,
        Customer.phone_number,
        Customer.address,
        Customer.is_active,
    ]
    column_searchable_list = [Customer.full_name, Customer.phone_number]
    name = "Customer"
    icon = "fa-solid fa-users"


class PaymentHistoryAdmin(ModelView, model=PaymentHistory):
    column_list = [
        PaymentHistory.id,
        PaymentHistory.amount,
        PaymentHistory.note,
        PaymentHistory.customer_id,
    ]
    name = "Payment History"
    icon = "fa-solid fa-money-bill"
