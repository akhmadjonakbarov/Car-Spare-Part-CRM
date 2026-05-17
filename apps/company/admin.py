from sqladmin import ModelView
from .models import Company


class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.id, Company.name, ]
    column_searchable_list = [Company.name, ]
    name = "Company"
    icon = "fa-solid fa-building"
