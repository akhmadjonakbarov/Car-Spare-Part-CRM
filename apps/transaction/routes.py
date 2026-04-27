from decimal import Decimal
from typing import List, Optional, Literal

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import asc, desc, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .helpers import TransactionHelper
from .schemas import TransactionOut, TransactionCreate, TransactionUpdate
from .models import Transaction
from di.db import db_dependency
from di.user import user_dependency

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# ----------------------------
#        CRUD Endpoints
# ----------------------------

@router.get(
    "",
    response_model=List[TransactionOut],
    summary="List transactions with pagination & optional filtering"
)
async def get_transactions(
        db: db_dependency,
        user: user_dependency,
        customer_id: Optional[int] = Query(None, ge=1, description="Filter by customer id"),
        min_amount: Optional[Decimal] = Query(None, description="Filter: amount ≥ min_amount"),
        max_amount: Optional[Decimal] = Query(None, description="Filter: amount ≤ max_amount"),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        sort_by: Literal["id", "customer_id", "amount"] = Query("id"),
        order: Literal["asc", "desc"] = Query("asc"),
):
    try:
        sort_column = {
            "id": Transaction.id,
            "customer_id": Transaction.customer_id,
            "amount": Transaction.amount
        }[sort_by]

        stmt = select(Transaction)

        if customer_id is not None:
            stmt = stmt.filter(Transaction.customer_id == customer_id)
        if min_amount is not None:
            stmt = stmt.filter(Transaction.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.filter(Transaction.amount <= max_amount)

        stmt = stmt.order_by(asc(sort_column) if order == "asc" else desc(sort_column))
        stmt = stmt.offset(offset).limit(limit)

        result = await db.execute(stmt)
        items = result.scalars().all()
        return items

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Get a single transaction by id"
)
async def get_transaction(
        transaction_id: int,
        db: db_dependency,
        user: user_dependency
):
    obj = await TransactionHelper.get_transaction_or_404(db, transaction_id)
    return obj


@router.get(
    "/by-customer/{customer_id}",
    response_model=List[TransactionOut],
    summary="List transactions for a specific customer"
)
async def get_transaction_by_customer(
        customer_id: int,
        db: db_dependency,
        user: user_dependency,
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        sort_by: Literal["id", "amount"] = Query("id"),
        order: Literal["asc", "desc"] = Query("asc"),
):
    sort_column = Transaction.id if sort_by == "id" else Transaction.amount

    stmt = (
        select(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(asc(sort_column) if order == "asc" else desc(sort_column))
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
)
async def create_transaction(
        payload: TransactionCreate,
        db: db_dependency,
        user: user_dependency
):
    try:
        return await TransactionHelper.apply_payment(db, payload.customer_id, payload.amount)
    except Exception as e:
        print(e)
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Replace an existing transaction (full update)"
)
async def replace_transaction(
        transaction_id: int,
        payload: TransactionCreate,
        db: db_dependency,
        user: user_dependency
):
    obj = await TransactionHelper.get_transaction_or_404(db, transaction_id)

    obj.customer_id = payload.customer_id
    obj.amount = payload.amount
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Partially update a transaction"
)
async def update_transaction(
        transaction_id: int,
        payload: TransactionUpdate,
        db: db_dependency,
        user: user_dependency
):
    obj = await TransactionHelper.get_transaction_or_404(db, transaction_id)

    if payload.customer_id is not None:
        obj.customer_id = payload.customer_id
    if payload.amount is not None:
        obj.amount = payload.amount

    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction"
)
async def delete_transaction(
        transaction_id: int,
        db: db_dependency,
        user: user_dependency
):
    obj = await TransactionHelper.get_transaction_or_404(db, transaction_id)
    await db.delete(obj)
    await db.commit()
