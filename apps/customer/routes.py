from decimal import Decimal
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from apps.customer.models import Customer, PaymentHistory
from apps.customer.schemas import CustomerCreate, PaymentHistoryScheme, CustomerRead
from di.db import db_dependency
from di.user import user_dependency
from utils.response_type import response_list, res_message
from apps.transaction.models import Transaction
from apps.purchase.models import Purchase
from apps.transaction.schemas import TransactionRead

router = APIRouter(
    prefix="/customers",
    tags=["Customer Management"],
)


@router.get("", response_model=List[CustomerRead], status_code=status.HTTP_200_OK)
async def get_customers(db: db_dependency):
    try:
        query = (
            select(Customer).where(Customer.is_deleted == False).options(
                selectinload(Customer.purchases).selectinload(
                    Purchase.document)
            ).order_by(desc('created_at'))
        )
        result = await db.execute(query)
        customers = result.scalars().all()

        modified_customers = []

        for customer in customers:
            customer_dict = {
                "id": customer.id,
                "full_name": customer.full_name,
                "phone_number": customer.phone_number,
                "phone_number2": customer.phone_number2,
                "address": customer.address,
                "total_debt": Decimal("0.0")
            }
            for purchase in customer.purchases:
                if purchase.is_debt:
                    customer_dict["total_debt"] += purchase.remain_money
                    print(f"[+] Purchase: {purchase}")
            modified_customers.append(
                customer_dict
            )

        sorted_customers = sorted(
            modified_customers, key=lambda x: x["total_debt"], reverse=True)

        return sorted_customers
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=CustomerRead)
async def add_customer(db: db_dependency, user: user_dependency, customer_create: CustomerCreate):
    try:
        existed_customer = await db.execute(
            select(Customer).where(Customer.phone_number ==
                                   customer_create.phone_number)
        )
        if existed_customer.scalar():
            raise HTTPException(
                status_code=400, detail="Customer already exists")

        new_customer = Customer(
            full_name=customer_create.full_name,
            address=customer_create.address,
            phone_number=customer_create.phone_number,
            phone_number2=customer_create.phone_number2,
            user_id=user.get("id"),
        )

        db.add(new_customer)
        await db.commit()
        await db.refresh(new_customer)
        return new_customer
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/update/{customer_id}", status_code=status.HTTP_200_OK, response_model=CustomerRead)
async def update_customer(
        db: db_dependency, user: user_dependency, customer_id: int, customer_update: CustomerCreate
):
    try:
        # 1. Fetch with relationships immediately so we have them after update
        query = (
            select(Customer)
            .where(Customer.id == customer_id)
            .options(selectinload(Customer.purchases).selectinload(Purchase.document))
        )
        result = await db.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # 2. Update attributes
        customer.full_name = customer_update.full_name
        customer.address = customer_update.address
        customer.phone_number = customer_update.phone_number
        customer.phone_number2 = customer_update.phone_number2

        # 3. Commit the changes
        await db.commit()

        result = await db.execute(query)
        customer = result.scalar_one()

        # 5. Build the response
        total_debt = Decimal("0.0")
        for purchase in customer.purchases:
            if purchase.is_debt:
                total_debt += Decimal(str(purchase.remain_money))

        return {
            "id": customer.id,
            "full_name": customer.full_name,
            "phone_number": customer.phone_number,
            "phone_number2": customer.phone_number2,
            "address": customer.address,
            "total_debt": total_debt
        }

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(db: db_dependency, user: user_dependency, customer_id: int):
    try:
        async with db.begin():
            query = (
                select(Customer).where(Customer.id == customer_id)
            )
            result = await db.execute(query)
            customer = result.scalar_one_or_none()
            if not customer:
                raise HTTPException(
                    status_code=404, detail="Customer not found")

            customer.soft_delete()

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{customer_id}/transactions", status_code=status.HTTP_200_OK, response_model=List[TransactionRead])
async def get_transactions(db: db_dependency, user: user_dependency, customer_id: int):
    try:
        query = (
            select(Transaction).where(
                Transaction.customer_id == customer_id,
                Transaction.is_deleted == False,
            ).order_by(desc(Transaction.created_at))
        )
        result = await db.execute(
            query
        )
        transactions = result.scalars().all()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payment-histories/add", status_code=status.HTTP_201_CREATED)
async def add_payment_history(db: db_dependency, payment_history_body: PaymentHistoryScheme):
    try:
        payment_history = PaymentHistory(**payment_history_body.model_dump())
        db.add(payment_history)
        await db.commit()
        return {
            "message": "Payment was added"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/payment-histories/{history_id}", status_code=status.HTTP_200_OK)
async def delete_payment_history(db: db_dependency, history_id: int):
    try:
        result = await db.execute(select(PaymentHistory).where(PaymentHistory.id == history_id))
        payment_history = result.scalar_one_or_none()
        if not payment_history:
            raise HTTPException(
                status_code=404, detail="PaymentHistory not found")

        payment_history.soft_delete()
        await db.commit()
        return {
            "message": "PaymentHistory was deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
