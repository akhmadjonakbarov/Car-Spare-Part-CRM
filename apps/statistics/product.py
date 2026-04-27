from apps.document.models import DocumentItemBalance
from apps.product_manager.models import Item

from typing import List, Dict, Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from apps.currency.models import Currency
from di.db import get_db
from di.user import get_current_user

router = APIRouter()


@router.get('/product-price-qty-report')
async def product_report(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user)]
):
    units: Dict[str, float] = {}
    total_uzs = 0.0
    total_usd = 0.0
    results = []

    # Fetch all products with related item and unit eagerly
    result = await db.execute(
        select(DocumentItemBalance)
        .options(
            selectinload(DocumentItemBalance.item).selectinload(Item.unit)
        )
    )

    products: List[DocumentItemBalance] = result.scalars().all()

    if products:
        for product in products:
            item = product.item
            if item.currency_type.lower() == 'usd':
                # Get currency asynchronously
                currency_result = await db.execute(
                    select(Currency)
                    .where(Currency.id == product.currency_id)
                )
                currency = currency_result.scalars().first()
                total_uzs += float((product.income_price * (currency.value if currency else 1)) * product.qty)
            else:
                total_uzs += float(product.income_price * product.qty)

            unit_value = item.unit.value if item.unit else "dona"
            units[unit_value] = units.get(unit_value, 0) + product.qty

        # Get latest currency rate
        currency_result = await db.execute(
            select(Currency)
            .where(Currency.is_deleted == False)
            .order_by(Currency.created_at.desc())
        )
        latest_currency = currency_result.scalars().first()
        total_usd = round(total_uzs / float(latest_currency.value if latest_currency else 1), 2)

        for key, value in units.items():
            results.append({
                'unit': key,
                'qty': value,
            })

    return {
        'units': results if results else [{'unit': 'dona', 'qty': 0.0}],
        'price': {
            'usd': total_usd,
            'uzs': total_uzs,
        }
    }
