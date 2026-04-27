import datetime

from pydantic import BaseModel, Field


class CurrencyTypeScheme(BaseModel):
    name: str = Field(max_length=10)


class CurrencyCreate(BaseModel):
    value: float = Field(
        gt=0, description="Currency value", default=12000
    )


class CurrencyBase(BaseModel):
    value: float

    class Config:
        from_attributes = True


class CurrencyRead(CurrencyBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CurrencyUpdate(CurrencyBase):
    pass
