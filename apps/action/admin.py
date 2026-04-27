from sqladmin import ModelView
from .models import Action


class ActionAdmin(ModelView, model=Action):
    column_list = [Action.id, Action.name, Action.status, Action.fixed_name]
    column_searchable_list = [Action.name]
    name = "Action"
    icon = "fa-solid fa-bolt"
