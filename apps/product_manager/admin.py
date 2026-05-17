from sqladmin import ModelView
from .models import Item, Category, Unit, Type, TypeItem, Car


class ItemAdmin(ModelView, model=Item):
    column_list = [
        Item.id,
        Item.name,
        Item.barcode,
        "car.name",
        "types",
        Item.income_price,
        Item.sale_price,
        Item.currency_type,
    ]
    column_searchable_list = [Item.name, Item.barcode]
    name = "Item"
    icon = "fa-solid fa-box"
    # Sort by ID in descending order to show newest items first
    column_default_sort = [(Item.id, True)]  # True means DESC (descending)


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]
    column_searchable_list = [Category.name]
    name = "Category"
    icon = "fa-solid fa-tags"


class UnitAdmin(ModelView, model=Unit):
    column_list = [Unit.id, Unit.value]
    column_searchable_list = [Unit.value]
    name = "Unit"
    icon = "fa-solid fa-balance-scale"


class TypeAdmin(ModelView, model=Type):
    column_list = [Type.id, Type.name]
    column_searchable_list = [Type.name]
    name = "Type"
    icon = "fa-solid fa-layer-group"


class TypeItemAdmin(ModelView, model=TypeItem):
    column_list = [TypeItem.type_id, TypeItem.item_id]
    name = "Type Item"
    icon = "fa-solid fa-link"


class CarAdmin(ModelView, model=Car):
    column_list = [Car.id, Car.name]
    column_searchable_list = [Car.name]
    name = "Car"
    icon = "fa-solid fa-car"
