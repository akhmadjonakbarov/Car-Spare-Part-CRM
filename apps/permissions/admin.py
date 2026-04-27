from sqladmin import ModelView
from .models import Permission


class PermissionAdmin(ModelView, model=Permission):
    column_list = [Permission.id, Permission.role_id, Permission.action_id]
    name = "Permission"
    icon = "fa-solid fa-lock"
