from typing import Optional
from pydantic import BaseModel
from marshmallow import fields, Schema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.document.models import DocumentItemBalance
from apps.base.schemas import BaseSchema
from apps.product_manager.models import Category, Car


class CategorySerializer(BaseSchema):
    name = fields.Str()
    items_type_count = fields.Method("get_items_type_count")
    items_count = fields.Method("get_items_count")

    @classmethod
    def get_items_type_count(cls, category: Category):
        return len(category.items)

    @classmethod
    def get_items_count(cls, category: Category):
        items_count = len(
            [item for item in category.items if len(item.document_items) > 0]) or 0
        return items_count


class CarRead(BaseModel):
    id: int
    name: str


class ItemSerializer(Schema):
    id = fields.Int()
    name = fields.Str()
    car = fields.Method("get_car_name")
    barcode = fields.Str()
    category = fields.Method("get_category_name")
    sub_category = fields.Method("get_sub_category_name")
    income_price = fields.Float()
    sale_price = fields.Float()
    unit = fields.Method("get_unit_value")
    currency_type = fields.Str()
    company = fields.Method("get_company_name")
    # currency_rate = fields.Method("get_currency_rate")
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    @classmethod
    def get_car_name(cls, obj):
        return obj.car.name if obj.car else None

    @classmethod
    def get_category_name(cls, obj):
        return obj.category.name if obj.category else None

    @classmethod
    def get_sub_category_name(cls, obj):
        return obj.sub_category.name if obj.sub_category else None

    @classmethod
    def get_unit_value(cls, obj):
        return obj.unit.value if obj.unit else None

    @classmethod
    def get_company_name(cls, obj):
        return obj.company.name if obj.company else None

    # @classmethod
    # def get_currency_rate(cls, obj):
    #     from apps.product_manager.models import DocumentItemBalance
    #     db = next(get_db())
    #     if obj.currency_type.lower() not in 'usd':
    #         return None
    #     balance = db.query(DocumentItemBalance).filter_by(item_id=obj.id).first()
    #     if balance is None:
    #         return None
    #     if balance.currency is None:
    #         return None
    #     return balance.currency.value

    # @classmethod
    # def get_currency_rate(cls, obj):
    #     # no DB query here — we assume currency info is preloaded
    #     if not obj or not hasattr(obj, "currency_type"):
    #         return None
    #
    #     if obj.currency_type.lower() != "usd":
    #         return None
    #     print(obj.document_item_balances.currency_rate_value)
    #     return 0.0
    #     # balance = getattr(obj, "document_item_balances", None)
    #     # if not balance or not getattr(balance, "currency", None):
    #     #     return None
    #     #
    #     # return balance.currency.value


class ItemOut(BaseModel):
    id: int
    name: str
    barcode: str
    sale_price: float
    income_price: float
    currency_type: str
    currency_rate: Optional[float] = None

    @classmethod
    async def from_orm_async(cls, obj, db: AsyncSession):
        rate = None
        if obj.currency_type.lower() == "usd":
            result = await db.execute(select(DocumentItemBalance).filter_by(item_id=obj.id))
            balance = result.scalar_one_or_none()
            if balance and balance.currency:
                rate = balance.currency.value
        return cls(
            id=obj.id,
            name=obj.name,
            barcode=obj.barcode,
            sale_price=obj.sale_price,
            income_price=obj.income_price,
            currency_type=obj.currency_type,
            currency_rate=rate,
        )
