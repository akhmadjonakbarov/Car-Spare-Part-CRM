from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, Numeric

from apps.base.schemas import BaseModelSchema
from apps.customer.schemas import CustomerRead


class TransactionBase(BaseModel):
    customer_id: int = Field(..., ge=1)
    amount: Decimal = Field(..., description="Amount with 3 decimal places")

    @validator("amount")
    def normalize_amount(cls, v: Decimal) -> Decimal:
        # Ensure exactly 3 decimal places to match Numeric(15,3)
        return v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    customer_id: Optional[int] = Field(None, ge=1)
    amount: Optional[Decimal]

    @validator("amount")
    def normalize_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is None:
            return v
        return v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


class TransactionOut(TransactionBase):
    id: int

    # class Config:
    #     orm_mode = True


class TransactionRead(BaseModelSchema):
    amount: float
