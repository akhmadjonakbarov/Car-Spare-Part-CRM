from fastapi import APIRouter, HTTPException, Path, Query
from starlette import status
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from apps.document.models import DocumentItem, Document, DocumentItemBalance
from apps.product_manager.models import Item
from di.db import db_dependency
from di.user import user_dependency
from utils.response_type import *
from .serializers.doc_item_serializers import DocumentItemSerializer
from apps.purchase.models import Purchase

router = APIRouter(
    prefix="/doc-item",
    tags=["Document Item Management"],
)


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_products(
        db: db_dependency, user: user_dependency, document_id: int | None = None,
        # page: int = Query(1, ge=1, description="Page number"),
        # page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    serializer = DocumentItemSerializer(many=True)

    query = select(DocumentItem).where(DocumentItem.is_deleted == False).options(
        selectinload(DocumentItem.item).selectinload(Item.unit), selectinload(DocumentItem.currency),
    )

    if document_id is not None:
        query = query.where(DocumentItem.document_id == document_id)

    result = await db.execute(query)
    doc_items = result.scalars().all()

    return serializer.dump(doc_items)


@router.delete("/delete/{doc_item_id}", status_code=status.HTTP_200_OK)
async def delete_product(
        db: db_dependency,
        user: user_dependency,
        doc_item_id: int = Path(..., description="ID of the document item to delete"),
):
    try:
        # 1. Use join or specific select to ensure doc_item isn't already soft-deleted
        result = await db.execute(
            select(DocumentItem)
            .where(DocumentItem.id == doc_item_id, DocumentItem.is_deleted == False)
        )
        doc_item = result.scalar_one_or_none()

        if not doc_item:
            raise HTTPException(status_code=404, detail="Item not found or already deleted")

        # 2. Atomic Balance Restore (Prevents Race Conditions)
        balance_result = await db.execute(
            update(DocumentItemBalance)
            .where(
                DocumentItemBalance.item_id == doc_item.item_id,
                DocumentItemBalance.sale_price == doc_item.sale_price,
                DocumentItemBalance.item_type == doc_item.item_type
            )
            .values(qty=DocumentItemBalance.qty + doc_item.qty)
        )

        if balance_result.rowcount == 0:
            # Handle case where balance record was missing
            raise HTTPException(status_code=404, detail="Balance record missing")

        # 3. Handle Document Cleanup
        # Fetch document and items count in one go
        doc_result = await db.execute(
            select(Document)
            .where(Document.id == doc_item.document_id)
            .options(selectinload(Document.document_items))
        )
        document = doc_result.scalar_one_or_none()

        # Logic check: Only delete document if this IS the last active item
        active_items = [i for i in document.document_items if not i.is_deleted]
        if len(active_items) == 1 and active_items[0].id == doc_item.id:
            # Perform cleanup of Purchase/Document
            purchase_result = await db.execute(select(Purchase).where(Purchase.document_id == document.id))
            purchase = purchase_result.scalar_one_or_none()
            if purchase:
                await db.delete(purchase)  # Using standard delete if hard_delete isn't a custom method
            document.soft_delete()

        # 4. Finalize
        doc_item.soft_delete()
        await db.commit()

        return {"status": "success", "message": "Item removed and stock restored"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        print(e)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
