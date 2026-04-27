from marshmallow import Schema, fields
from apps.document.models import Document, DocumentItem


class DocumentSerializer(Schema):
    id = fields.Int()
    doc_type = fields.Str()
    type_of_items = fields.Method('get_type_of_items')
    count_of_items = fields.Method('get_count_of_items')
    price = fields.Method('get_price')
    discount = fields.Method("get_discount")
    created_at = fields.DateTime()

    @classmethod
    def get_type_of_items(cls, document: Document):
        return len(document.document_items)

    @classmethod
    def get_count_of_items(cls, document: Document):
        total_qty = 0.0
        for item in document.document_items:
            total_qty += float(item.qty)
        return total_qty

    @classmethod
    def get_discount(cls, document: Document):
        return document.discount

    @classmethod
    def get_price(cls, document: Document):
        total_uzs = 0.0
        items = document.document_items
        for i in range(len(items)):
            item: DocumentItem = items[i]
            if item.item.currency_type.lower() == 'usd':
                currency_value_rate = item.currency_rate_value
                total_uzs = total_uzs + float(
                    (float(item.sale_price) * float(currency_value_rate) * float(item.qty)))
            else:
                total_uzs = total_uzs + float((item.sale_price * item.qty))

        return total_uzs
