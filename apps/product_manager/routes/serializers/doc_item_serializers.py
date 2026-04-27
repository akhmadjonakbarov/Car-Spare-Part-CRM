from marshmallow import fields, Schema
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
