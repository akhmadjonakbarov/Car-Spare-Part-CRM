from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy import select, desc, func
from starlette import status

from apps.currency.models import Currency
from apps.currency.schemas import CurrencyRead, CurrencyCreate, CurrencyUpdate
from di.db import db_dependency
from di.user import user_dependency
from utils.pagination import pagination, PostPagination, get_total_pages
from utils.response_type import *

router = APIRouter(
    prefix="/currencies",
    tags=["Currency Management"]
)


@router.get(
    "/",
    response_model=PostPagination[CurrencyRead]
)
async def get_currencies(
        db: db_dependency,
        # user: user_dependency = user_dependency,
        pagination_param: dict = Depends(pagination)
):
    """
    Get all currencies with pagination.
    """
    try:
        # 1. Base Query (Filtered)
        base_query = select(Currency).where(Currency.is_deleted == False)

        # 2. Get Total Count (Database side)
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        pages = await get_total_pages(total, pagination_param['limit'])

        query = select(Currency).where(Currency.is_deleted == False).order_by(desc(Currency.created_at))

        # 3. Get Paginated Data
        data_query = (
            base_query
            .order_by(desc(Currency.created_at))
            .offset(pagination_param['skip'])
            .limit(pagination_param['limit'])
        )

        result = await db.execute(data_query)
        items = result.scalars().all()

        return Response(total, pages, pagination_param['page'], pagination_param['skip'], items).paginated_response()


    except Exception as e:
        return res_error(error=str(e))


#
@router.post('/add', response_model=CurrencyRead, status_code=status.HTTP_201_CREATED)
async def add_currency(

        currency_create: CurrencyCreate,
        db: db_dependency = db_dependency,
        user: user_dependency = user_dependency,
):
    try:
        new_currency = Currency(
            **currency_create.model_dump(),
            user_id=user.get('id')
        )
        db.add(new_currency)
        await db.commit()
        await db.refresh(new_currency)
        return new_currency
        # Update related products
        # result = await db.execute(
        #     select(DocumentItemBalance)
        #     .join(DocumentItemBalance.item)
        #     .filter(Item.currency_type == 'usd')
        # )
        # store_products = result.scalars().all()

        # for product in store_products:
        #     product.currency_rate_value = new_currency.value
        #     product.currency_id = new_currency.id
        #     db.add(product)
        #     await db.flush()


    except Exception as e:
        await db.rollback()
        return res_error(error=str(e))


#
@router.patch('/update/{currency_id}', response_model=CurrencyRead, status_code=status.HTTP_200_OK)
async def update_currency(
        currency_update: CurrencyUpdate,
        db: db_dependency = db_dependency,
        currency_id: int = Path(gt=0),
):
    try:
        query = select(Currency).where(Currency.id == currency_id)
        result = await db.execute(query)
        updated_currency = result.scalar_one_or_none()

        if not updated_currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Currency not found"
            )

        updated_currency.value = currency_update.value
        await db.commit()
        await db.refresh(updated_currency)
        return updated_currency
    except Exception as e:
        return res_error(error=str(e))


@router.delete('/delete/{currency_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_currency(
        db: db_dependency,
        currency_id: int = Path(gt=0)
):
    try:
        async with db.begin():
            result = await db.execute(select(Currency).filter_by(id=currency_id))
            currency = result.scalar_one_or_none()

            if not currency:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Currency not found"
                )

            currency.soft_delete()

    except HTTPException:
        raise
    except Exception as e:
        return res_error(error=str(e))
