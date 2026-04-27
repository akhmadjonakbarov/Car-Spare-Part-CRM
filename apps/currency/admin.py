from sqladmin import ModelView
from .models import Currency


class CurrencyAdmin(ModelView, model=Currency):
    column_list = [Currency.id, Currency.value, Currency.user_id]
    name = "Currency"
    icon = "fa-solid fa-money-currency-dollar"
