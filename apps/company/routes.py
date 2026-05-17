from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy import select, desc, func
from starlette import status

from apps.company.models import Company
from apps.company.schemas import CompanyRead, CompanyCreate, CompanyUpdate
from di.db import db_dependency
from di.user import user_dependency
from utils.pagination import pagination, PostPagination, get_total_pages
from utils.response_type import *

router = APIRouter(
    prefix="/companies",
    tags=["Company Management"]
)


@router.get("/", response_model=PostPagination[CompanyRead])
async def get_companies(
        db: db_dependency,
        pagination_param: dict = Depends(pagination)
):
    try:
        base_query = select(Company).where(Company.is_deleted == False)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        pages = await get_total_pages(total, pagination_param['limit'])

        data_query = (
            base_query
            .order_by(desc(Company.created_at))
            .offset(pagination_param['skip'])
            .limit(pagination_param['limit'])
        )

        result = await db.execute(data_query)
        items = result.scalars().all()

        return Response(total, pages, pagination_param['page'], pagination_param['skip'], items).paginated_response()

    except Exception as e:
        return res_error(error=str(e))


@router.post('/add', response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def add_company(
        company_create: CompanyCreate,
        db: db_dependency = db_dependency,
        user: user_dependency = user_dependency,
):
    try:
        new_company = Company(
            **company_create.model_dump(exclude_none=True),
            user_id=user.get('id')
        )
        db.add(new_company)
        await db.commit()
        await db.refresh(new_company)
        return new_company

    except Exception as e:
        await db.rollback()
        return res_error(error=str(e))


@router.patch('/update/{company_id}', response_model=CompanyRead, status_code=status.HTTP_200_OK)
async def update_company(
        company_update: CompanyUpdate,
        db: db_dependency = db_dependency,
        company_id: int = Path(gt=0),
):
    try:
        query = select(Company).where(Company.id == company_id)
        result = await db.execute(query)
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        update_data = company_update.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(company, field, value)

        await db.commit()
        await db.refresh(company)
        return company

    except Exception as e:
        return res_error(error=str(e))


@router.delete('/delete/{company_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
        db: db_dependency,
        company_id: int = Path(gt=0)
):
    try:
        async with db.begin():
            result = await db.execute(select(Company).filter_by(id=company_id))
            company = result.scalar_one_or_none()

            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )

            company.soft_delete()

    except HTTPException:
        raise
    except Exception as e:
        return res_error(error=str(e))
