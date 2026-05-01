from datetime import datetime

from marshmallow import Schema, fields
from pydantic import BaseModel, field_validator, field_validator
from apps.product_manager.routes.serializers.common_serializers import ItemSerializer
from apps.product_manager.schemas.product import ProductRead

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class StoreSchemaRead(BaseModel):
    id: int
    item: ProductRead
    item_type: str | None
    currency_rate_value: float | None = 0.0  # Allows None if DB value is null
    income_price: float
    sale_price: float
    sale_percentage: float
    qty: float
    created_at: datetime  # Automatically serializes datetime objects to strings
    updated_at: datetime

    @field_validator("currency_rate_value", mode="before")
    @classmethod
    def prevent_none(cls, v):
        return v if v is not None else 0.0

    # This allows Pydantic to read data from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)
