from typing import List
from typing import Optional
from pydantic import BaseModel, Field




class ItemCreateScheme(BaseModel):
    name: str = Field()
    car_id: Optional[int] = Field(default=None)
    barcode: str = Field()
    category_id: int = Field(gt=0)
    sub_category_id: Optional[int] = Field(default=None)
    income_price: float = Field(default=0.0)
    sale_price: float = Field(default=0.0)
    unit_id: int = Field(gt=0)
    currency_type: str = Field(default="uzs")
    type_ids: Optional[List[int]] = Field(None)


class ItemUpdateScheme(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2)
    car_id: Optional[int] = Field(default=None)
    barcode: Optional[str] = Field(default=None, min_length=2)
    category_id: int = Field(gt=0)
    sub_category_id: Optional[int] = Field(default=None)
    income_price: Optional[float] = Field(default=None)
    sale_price: Optional[float] = Field(default=None)
    unit_id: int = Field(gt=0)
    currency_type: Optional[str] = Field(default=None)
    type_ids: List[int] = Field(None)


class ItemDeleteScheme(BaseModel):
    type_name: str = Field(default=None)


class UnitScheme(BaseModel):
    value: str


class CarScheme(BaseModel):
    name: str = Field(min_length=2)


class CategoryScheme(BaseModel):
    name: str = Field(min_length=4)


class SubCategoryScheme(BaseModel):
    name: str = Field(min_length=2)
    category_id: int = Field(gt=0)


# Schema for the Currency object
class CurrencyScheme(BaseModel):
    id: Optional[int] = Field(None, description="Currency ID")


# Main schema for Document Item
class DocumentItemModelScheme(BaseModel):
    qty: float = Field(..., description="Quantity")
    item_id: int = Field(..., description="Item details")
    item_type: Optional[str] = Field(None, description="Type of item")


class BuyDocumentModelScheme(BaseModel):
    products: List[DocumentItemModelScheme] = Field(
        ..., description="List of product document items"
    )


class Item(BaseModel):
    id: Optional[int] = Field(None, description="Item ID")
    name: str = Field(min_length=4)
    barcode: str = Field(min_length=4)


class SellProduct(BaseModel):
    item_id: int = Field(None, description="Item ID")
    qty: Optional[int] = Field(default=0.0)
    item_type: Optional[str] = Field(None, description="Type of Item")
    discount: float = Field(default=0.0)


class SellDocumentModelScheme(BaseModel):
    sold_products: List[SellProduct] = Field(
        ..., description="List of product document items"
    )
    customer_id: int = Field(None, description="Customer ID")
    is_debt: bool = Field(default=False, description="Is debt or not")
    remain_money: float = Field(description="Remain Money", default=0.0)
    discount: float = Field(default=0.0, description="Discount")


class DocumentItemBalanceUpdatedScheme(BaseModel):
    qty: Optional[int] = None
    income_price: Optional[float] = None
    selling_price: Optional[float] = None
    selling_percentage: Optional[float] = None
