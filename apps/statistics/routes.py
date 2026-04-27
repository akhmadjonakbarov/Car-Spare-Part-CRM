from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, case, select

from utils.response_type import response_list
from apps.document.models import DocumentItem, Document
from apps.product_manager.models import Item, Unit
from .profit import router as profit_router
from .sales_rate import router as sales_rate_router
from .product import router as product_router
from di.db import db_dependency

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics Management"],
)

router.include_router(profit_router)
router.include_router(sales_rate_router)
router.include_router(product_router)


@router.get('/report', status_code=status.HTTP_200_OK)
async def report(db: db_dependency):
    """
    Generate product-based report with income, sale, and profit statistics.
    """
    try:
        stmt = (
            select(
                Item.name.label("name"),
                Unit.value.label("unit"),
                func.coalesce(
                    func.sum(
                        case(
                            (DocumentItem.qty > 0, DocumentItem.qty),
                            else_=0
                        )
                    ),
                    0
                ).label("total_qty"),
                func.coalesce(
                    func.sum(
                        case(
                            (Item.currency_type == "usd",
                             DocumentItem.qty * DocumentItem.income_price * DocumentItem.currency_rate_value),
                            else_=(DocumentItem.qty * DocumentItem.income_price)
                        )
                    ),
                    0
                ).label("total_income"),
                func.coalesce(
                    func.sum(
                        case(
                            (Item.currency_type == "usd",
                             DocumentItem.qty * DocumentItem.sale_price * DocumentItem.currency_rate_value),
                            else_=(DocumentItem.sale_price * DocumentItem.qty)
                        )
                    ),
                    0
                ).label("total_sale"),
            )
            .join(Unit, Unit.id == Item.unit_id)
            .outerjoin(DocumentItem, DocumentItem.item_id == Item.id)
            .outerjoin(Document, Document.id == DocumentItem.document_id)
            .filter(
                ((Document.is_deleted.is_(False)) & (Document.doc_type == "sell"))
                | (Document.id.is_(None))
            )
            .filter(DocumentItem.is_deleted.is_(False) | (DocumentItem.id.is_(None)))
            .group_by(Item.id, Item.name, Unit.value)
        )

        result = await db.execute(stmt)
        products = result.all()

        result_list = [
            {
                "name": "best_selling",
                "value": [
                    {
                        "name": r.name,
                        "unit": r.unit,
                        "total_qty": r.total_qty,
                        "total_income": r.total_income,
                        "total_sale": r.total_sale,
                        "total_profit": r.total_sale - r.total_income,
                    }
                    for r in sorted(products, key=lambda x: x.total_qty, reverse=True)
                    if r.total_qty > 0
                ],
            },
            {
                "name": "not_selling",
                "value": [
                    {
                        "name": r.name,
                        "unit": r.unit,
                        "total_qty": r.total_qty,
                        "total_income": r.total_income,
                        "total_sale": r.total_sale,
                        "total_profit": r.total_sale - r.total_income,
                    }
                    for r in products if r.total_qty == 0
                ],
            },
            {
                "name": "much_selling_low_price",
                "value": [
                    {
                        "name": r.name,
                        "unit": r.unit,
                        "total_qty": r.total_qty,
                        "total_income": r.total_income,
                        "total_sale": r.total_sale,
                        "total_profit": r.total_sale - r.total_income,
                    }
                    for r in products if r.total_qty > 50 and r.total_sale < 10000
                ],
            },
            {
                "name": "low_selling_much_price",
                "value": [
                    {
                        "name": r.name,
                        "unit": r.unit,
                        "total_qty": r.total_qty,
                        "total_income": r.total_income,
                        "total_sale": r.total_sale,
                        "total_profit": r.total_sale - r.total_income,
                    }
                    for r in products if r.total_qty < 5 and r.total_sale > 50000
                ],
            },
        ]

        return response_list(lst=result_list)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/all', status_code=status.HTTP_200_OK)
async def all_statistics():
    return response_list(lst=[])
