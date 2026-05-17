from marshmallow import fields, Schema
from pydantic import BaseModel

from apps.product_manager.schemas.product import ProductRead
# from apps.currency.routes.serializers import CurrencySerializer


class ItemSerializer(Schema):
    id = fields.Int()
    name = fields.Str()
    barcode = fields.Str()
    unit = fields.Method("get_unit")
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    @classmethod
    def get_unit(cls, item):
        return item.unit.value


class DocumentItemSerializer(Schema):
    id = fields.Integer()
    item = fields.Nested(ItemSerializer, many=False)
    item_type = fields.Str(allow_none=True)
    # currency = fields.Nested(CurrencySerializer, many=False)
    sale_price = fields.Float()
    selling_percentage = fields.Float()
    income_price = fields.Float()
    qty = fields.Float()


class DocumenItemRead(BaseModel):
    id: int
    item: ProductRead
    item_type: str | None
    # currency: CurrencySerializer | None
    sale_price: float
    selling_percentage: float
    income_price: float
    qty: float