import os
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Path
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, mapped_column, Mapped

from apps.document.models import Document, DocumentItem
from apps.currency.models import Currency
from config.settings import settings

import asyncio

from di.db import db_dependency

router = APIRouter()

os.makedirs(f"{settings.FILES_DIR}/statistics", exist_ok=True)


@router.get('/daily-sales-rate')
async def daily_sales_rate(db: db_dependency):
    now = datetime.now()
    passed_week = now - timedelta(days=7)

    result = await db.execute(
        select(DocumentItem)
        .options(selectinload(DocumentItem.item))  # eager load related item
        .join(Document)
        .filter(
            Document.is_deleted == False,
            Document.doc_type == 'sell',
            DocumentItem.is_deleted == False,
        )
    )
    document_items = result.scalars().all()

    aggregated = {}

    for item in document_items:
        currency_type = item.item.currency_type.lower() if item.item else ''
        if currency_type == 'usd':
            converted_sale_price = item.sale_price * item.qty * item.currency_rate_value
            profit = (item.sale_price - item.income_price) * item.currency_rate_value * item.qty
        else:
            converted_sale_price = item.sale_price * item.qty
            profit = (item.sale_price - item.income_price) * item.qty

        created_date = item.created_at.date()

        if created_date not in aggregated:
            aggregated[created_date] = {'sales': 0.0, 'profit': 0.0}

        aggregated[created_date]['sales'] += float(converted_sale_price)
        aggregated[created_date]['profit'] += float(profit)

    results = [
        {"date": str(date), "sales": data["sales"], "profit": data["profit"]}
        for date, data in sorted(aggregated.items(), key=lambda x: x[0])
    ]

    return results


@router.get('/top-sales-products/{count}')
async def top_sales_products(
        db: db_dependency,
        count: int = Path(description="Count of top sales products"),
):
    result = await db.execute(
        select(DocumentItem)
        .join(Document)
        .filter(
            Document.is_deleted == False,
            Document.doc_type == 'sell',
            DocumentItem.is_deleted == False,
        )
        .order_by(desc(DocumentItem.qty))
    )
    document_items = result.scalars().all()

    data = []

    for item in document_items:
        total_profit = 0.0
        if item.item.income_currency.lower() == 'usd':
            currency_result = await db.execute(
                select(Currency).filter_by(id=item.currency_id)
            )
            currency = currency_result.scalar_one_or_none()
            if currency:
                total_profit += float((item.sale_price - (item.income_price * currency.value)) * item.qty)
        else:
            total_profit += float((item.sale_price - item.income_price) * item.qty)

        data.append({
            'item': str(item.item.name),
            'profit': total_profit,
            'date': item.created_at.strftime("%d/%m/%y")
        })
