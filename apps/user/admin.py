from sqladmin import ModelView
from .models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.first_name, User.last_name, User.is_active]
    column_searchable_list = [User.email, User.first_name, User.last_name]
    name = "User"
    icon = "fa-solid fa-user"
