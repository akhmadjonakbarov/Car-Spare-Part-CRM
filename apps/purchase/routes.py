from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from apps.document.models import Document, DocumentItem
from apps.purchase.models import Purchase
from di.db import db_dependency
from utils.response_type import res_message
from .schemas import PurchaseRead
from apps.product_manager.models import Item
from apps.transaction.models import Transaction

router = APIRouter(
    prefix="/purchases",
    tags=["Purchase Management"]
)


@router.get(
    "/", status_code=status.HTTP_200_OK,
    response_model=List[PurchaseRead]
)
async def get_purchases(
        db: db_dependency,
):
    try:
        base_query = (
            select(Purchase).where(Purchase.is_deleted == False).options(
                selectinload(Purchase.document)
                .selectinload(Document.document_items)
                .selectinload(DocumentItem.item)
                .options(
                    selectinload(Item.category),
                    selectinload(Item.sub_category),
                    selectinload(Item.unit),
                    selectinload(Item.car),
                ),
                selectinload(Purchase.document)
                .selectinload(Document.document_items)
                .selectinload(DocumentItem.currency)
            ).order_by(desc(Purchase.created_at))
        )
        result = await db.execute(base_query)
        purchases = result.scalars().all()

        return purchases

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/customer-purchases/{customer_id}", status_code=status.HTTP_200_OK,
    response_model=List[PurchaseRead]
)
async def customer_purchases(
        db: db_dependency,
        customer_id: int
):
    """
    Get all purchases for a specific customer.
    """
    try:

        query = (
            select(Purchase)
            .join(Document, Purchase.document_id == Document.id)
            .where(
                Purchase.customer_id == customer_id,
                Purchase.is_deleted == False,
                Document.is_deleted == False,
            ).options(
                selectinload(Purchase.document)
                .selectinload(Document.document_items)
                .selectinload(DocumentItem.item).options(
                    selectinload(Item.unit),
                    selectinload(Item.category),
                    selectinload(Item.sub_category),
                    selectinload(Item.car)
                )

            )
            .order_by(desc(Purchase.created_at))
        )
        result = await db.execute(query)
        purchases = result.scalars().all()

        return purchases

    except Exception as e:
        print(f"Error: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pay", status_code=status.HTTP_200_OK)
async def pay_purchase(
        db: db_dependency,
        customer_id: int = Query(..., description="Customer ID"),
        purchase_id: int = Query(..., description="Purchase ID"),
):
    """
    Mark a purchase as paid for a specific customer.
    """
    try:
        result = await db.execute(
            select(Purchase).where(
                Purchase.id == purchase_id,
                Purchase.customer_id == customer_id,
                Purchase.is_deleted == False,
            )
        )
        purchase: Purchase = result.scalar_one_or_none()

        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase not found for the given customer",
            )

        # Execute pay() safely
        if hasattr(purchase, "pay"):
            transaction = Transaction(
                customer_id=purchase.customer_id,
                purchase_id=purchase.id,
                amount=purchase.remain_money
            )
            db.add(transaction)
            await db.commit()

            purchase.pay()
        else:
            raise HTTPException(
                status_code=400, detail="Purchase model missing `pay()` method")

        db.add(purchase)
        await db.commit()
        await db.refresh(purchase)

        return {
            "message": f"Payment completed successfully for purchase ID {purchase.id}"
        }

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail=f"Database integrity error: {str(e)}")

    except HTTPException:
        await db.rollback()
        raise

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment failed: {str(e)}",
        )
