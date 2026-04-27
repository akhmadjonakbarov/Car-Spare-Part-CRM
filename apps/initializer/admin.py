from sqladmin import ModelView
from .models import Initializer


class InitializerAdmin(ModelView, model=Initializer):
    column_list = [Initializer.id, Initializer.value]
    name = "Initializer"
    icon = "fa-solid fa-play"
