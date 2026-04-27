from pydantic import BaseModel, field_validator

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List

from apps.base.schemas import BaseModelSchema


class TypeRead(BaseModelSchema):
    name: str

    class Config:
        from_attributes = True


class ProductRead(BaseModel):
    id: int
    name: str
    income_price: float
    sale_price: float
    barcode: str
    currency_type: str
    category: str
    unit: str
    # Fixed: Match the Pydantic field name to your logic or the DB attribute
    item_type: str | None = None

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


class ProductCreatedRes(BaseModel):
    id: int
    name: str
    income_price: float
    sale_price: float
    barcode: str
    currency_type: str
    category: str
    unit: str

    # Fixed: Match the Pydantic field name to your logic or the DB attribute

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
