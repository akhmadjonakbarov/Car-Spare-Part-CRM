from typing import List

from fastapi import APIRouter, HTTPException, status, Query

from apps.document.models import DocumentItemBalance

from apps.product_manager.schemes import DocumentItemBalanceUpdatedScheme
from apps.product_manager.models import Item
from di.db import db_dependency
from di.user import user_dependency
from utils.get_pagination import Pagination

from utils.response_type import *
from .serializers.store_serializers import StoreSchemaRead
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(
    prefix="/store",
    tags=["Store Management"],
)


@router.get("", status_code=status.HTTP_200_OK, response_model=List[StoreSchemaRead])
async def get_products_in_store(
        db: db_dependency,
        user: user_dependency,
):
    try:
        query = (select(DocumentItemBalance)
                 .options(
            selectinload(DocumentItemBalance.item).options(
                selectinload(Item.unit),
                selectinload(Item.category),
                selectinload(Item.sub_category),
                selectinload(Item.car),
                selectinload(Item.document_item_balances)
            ),
            selectinload(DocumentItemBalance.currency),
            selectinload(DocumentItemBalance.document)
        )
        )
        result = await db.execute(query)
        products = result.scalars().all()

        return products

    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get("/fetch", response_model=List[StoreSchemaRead], status_code=status.HTTP_200_OK)
async def get_store(db: db_dependency, user: user_dependency):
    try:
        result = await db.execute(
            select(DocumentItemBalance)
            .options(
                selectinload(DocumentItemBalance.item).options(
                    selectinload(Item.unit),
                    selectinload(Item.category),
                    selectinload(Item.sub_category),
                    selectinload(Item.car),
                    selectinload(Item.document_item_balances)
                ),
                selectinload(DocumentItemBalance.currency),
                selectinload(DocumentItemBalance.document)
            )
        )
        products = result.scalars().unique().all()

        return products

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: {str(e)}"
        )


@router.patch("/update-item-balance/{item_balance_id}", status_code=status.HTTP_200_OK)
async def update_item_balance(
        db: db_dependency,
        user: user_dependency,
        item_scheme: DocumentItemBalanceUpdatedScheme,
        item_balance_id: int
):
    try:
        async with db.begin():
            result = await db.execute(
                select(DocumentItemBalance).where(
                    DocumentItemBalance.id == item_balance_id)
            )
            item_balance = result.scalar_one_or_none()

            if not item_balance:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item balance not found"
                )

            # Update fields safely
            if item_scheme.qty is not None:
                item_balance.qty = item_scheme.qty
            if item_scheme.income_price is not None:
                item_balance.income_price = item_scheme.income_price
            if item_scheme.selling_price is not None:
                item_balance.sale_price = item_scheme.selling_price
            if item_scheme.selling_percentage is not None:
                item_balance.sale_percentage = item_scheme.selling_percentage

            await db.commit()
            await db.refresh(item_balance)

            return response_item(item_balance)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: {str(e)}"
        )
