from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, computed_field


class CustomerRead(BaseModel):
    id: int
    full_name: str
    phone_number: str
    phone_number2: Optional[str] = None
    address: str
    total_debt: float | None = None

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    full_name: str = Field(
        default="John Smith",
        description="Customer's full name", min_length=3
    )
    phone_number: str = Field(
        default="901237459",
        description="Customer's phone number", min_length=9
    )
    phone_number2: str | None = Field(
        default=None, description="Customer's secondary phone number",
    )
    address: Optional[str] = Field(
        description="Customer's address", default=None)


class PaymentHistoryScheme(BaseModel):
    amount: Decimal = Field()
    note: Optional[str] = Field()
    customer_id: int = Field()
