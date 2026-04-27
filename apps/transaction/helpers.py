from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import asc, select
from sqlalchemy.orm.query import Query
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from apps import Purchase, Transaction


class TransactionHelper:
    @staticmethod
    async def get_transaction_or_404(db: AsyncSession, transaction_id: int):
        from .models import Transaction
        query = (
            select(Transaction).where(Transaction.id == transaction_id)
        )
        result = await db.execute(query)
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {transaction_id} not found"
            )
        return transaction

    @staticmethod
    async def apply_payment(db: AsyncSession, customer_id: int, amount) -> dict:
        payment_incoming = Decimal(str(amount))
        payment_remaining = payment_incoming

        if payment_remaining <= 0:
            raise ValueError("Payment amount must be > 0")

        # 1. Fetch debt-eligible purchases with a Row Lock
        query = (
            select(Purchase)
            .filter(
                Purchase.customer_id == customer_id,
                Purchase.is_debt == True,
                Purchase.remain_money > 0
            )
            .order_by(asc(Purchase.id))
            .with_for_update()
        )

        result = await db.execute(query)
        purchases = result.scalars().all()
        allocations = []

        for purchase in purchases:
            if payment_remaining <= 0:
                break

            current_remain = Decimal(str(purchase.remain_money or 0))
            allocate = min(current_remain, payment_remaining)

            # Record the transaction
            txn = Transaction(
                customer_id=customer_id,
                purchase_id=purchase.id,
                amount=allocate,

            )
            db.add(txn)

            # Update Purchase
            purchase.remain_money -= allocate
            if purchase.remain_money <= 0:
                purchase.remain_money = Decimal("0.00")
                purchase.is_debt = False
                # If you have a paid_at timestamp, set it here
                # purchase.paid_at = datetime.utcnow()

            allocations.append({
                "purchase_id": purchase.id,
                "allocated": float(allocate),
                "remain_after": float(purchase.remain_money),
                "closed": not purchase.is_debt
            })

            payment_remaining -= allocate

        # 2. OPTIONAL: Handle Overpayment
        # If payment_remaining > 0, you could add it to a 'Customer.balance' column here
        # if payment_remaining > 0:
        #    customer = await db.get(Customer, customer_id)
        #    customer.balance += payment_remaining

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

        return {
            "customer_id": customer_id,
            "total_incoming": float(payment_incoming),
            "allocations": allocations,
            "unapplied_amount": float(payment_remaining)
        }
