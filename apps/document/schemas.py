from typing import List

from pydantic import BaseModel, field_validator

from apps.base.schemas import BaseModelSchema


class ProductRead(BaseModel):
    id: int
    name: str
    car: str
    barcode: str
    category: str
    sub_category: str | None = None
    income_price: float
    sale_price: float
    unit: str
    currency_type: str

    # 1. Fix the Unit object -> string error
    @field_validator('unit', mode='before')
    @classmethod
    def transform_unit(cls, v):
        if hasattr(v, 'value'):  # If it's the Unit object, get the .value
            return v.value
        return str(v)

    # 2. Fix the Category object -> string error
    @field_validator('category', mode='before')
    @classmethod
    def transform_category(cls, v):
        if hasattr(v, 'name'):  # If it's the Category object, get the .name
            return v.name
        return str(v)

    @field_validator('sub_category', mode='before')
    @classmethod
    def transform_sub_category(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return str(v) if v else None

    # 3. Fix the Car object -> string error
    @field_validator('car', mode='before')
    @classmethod
    def transform_car_rel(cls, v):
        if hasattr(v, 'name'):  # If it's the Car object, get the .name
            return v.name
        return str(v)


class DocumentItemRead(BaseModelSchema):
    item: ProductRead
    qty: float
    income_price: float
    sale_price: float
    sale_percentage: float
    currency_rate_value: float
    item_type: str | None = None


class DocumentRead(BaseModelSchema):
    document_items: List[DocumentItemRead]
