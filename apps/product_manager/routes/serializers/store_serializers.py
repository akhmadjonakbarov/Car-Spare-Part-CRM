from marshmallow import Schema, fields

from apps.product_manager.routes.serializers.common_serializers import ItemSerializer


class StoreSerializer(Schema):
    id = fields.Int()
    item = fields.Nested(ItemSerializer)
    item_type = fields.Str(allow_none=True)
    # currency = fields.Nested(CurrencySerializer)
    currency_rate_value = fields.Float()
    income_price = fields.Float()
    sale_price = fields.Float()
    sale_percentage = fields.Float()
    qty = fields.Float()
    # document = fields.Nested(DocumentSerializer)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
