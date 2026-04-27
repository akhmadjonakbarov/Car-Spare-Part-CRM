from typing import List

from apps.base.schemas import BaseModelSchema
from apps.product_manager.schemas.product import ProductRead


class DocumentItemRead(BaseModelSchema):
    item: ProductRead
    qty: float
    income_price: float
    sale_price: float
    sale_percentage: float
    currency_rate_value: float


class DocumentRead(BaseModelSchema):
    document_items: List[DocumentItemRead]
