from sqladmin import ModelView
from .models import Item, Company, Category, Unit, Type, TypeItem


class ItemAdmin(ModelView, model=Item):
    column_list = [
        Item.id,
        Item.name,
        Item.barcode,
        Item.income_price,
        Item.sale_price,
        Item.currency_type,
    ]
    column_searchable_list = [Item.name, Item.barcode]
    name = "Item"
    icon = "fa-solid fa-box"


class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.id, Company.name]
    column_searchable_list = [Company.name]
    name = "Company"
    icon = "fa-solid fa-building"


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
