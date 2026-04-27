import calendar
from collections import defaultdict

from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from di.db import db_dependency
from di.user import user_dependency
from apps.document.models import DocumentItem, Document

router = APIRouter()


@router.get("/profit/by-duration")
async def profit_by_duration(
        db: db_dependency, user: user_dependency,
        start_date: datetime = Query(...),
        end_date: datetime = Query(...)
):
    if end_date < start_date:
        raise HTTPException(
            status_code=400, detail="end_date must be after start_date")

    now = datetime.now()

    queryset = db.query(DocumentItem).filter(
        DocumentItem.created_at <= start_date,
        DocumentItem.created_at >= end_date,
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "profit": 0.0,
    }

@router.get("/profit/week")
async def profit_week(db: db_dependency):
    now = datetime.now()
    passed_week = now - timedelta(days=7)

    # Async query with eager load for related item
    result = await db.execute(
        select(DocumentItem)
        .options(selectinload(DocumentItem.item))
        .join(Document)
        .filter(
            Document.is_deleted == False,
            Document.doc_type == 'sell',
            DocumentItem.created_at.between(passed_week, now),
            DocumentItem.is_deleted == False
        )
    )
    document_items = result.scalars().all()

    # Group and sum profits by weekday
    daily_profits = defaultdict(float)
    for item in document_items:
        weekday_name = item.created_at.strftime("%A")  # e.g., "Monday"
        currency_type = item.item.currency_type.lower() if item.item else ''
        if currency_type == 'usd':
            daily_profits[weekday_name] += (
                (float(item.sale_price * item.currency_rate_value) -
                 float(item.income_price * item.currency_rate_value))
                * float(item.qty)
            )
        else:
            daily_profits[weekday_name] += (
                (float(item.sale_price) - float(item.income_price)) * float(item.qty)
            )

    # Sort days in week order
    week_days = list(calendar.day_name)
    result = [
        {"day": day, "profit": round(daily_profits.get(day, 0), 2)}
        for day in week_days
    ]

    return result