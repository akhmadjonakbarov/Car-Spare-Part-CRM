from fastapi import APIRouter, HTTPException, status
from fastapi import Query
from sqlalchemy import func, select

from sqlalchemy.exc import SQLAlchemyError

from apps.product_manager.models import Company
from apps.product_manager.schemes import CompanyScheme
from di.db import db_dependency
from utils.response_type import response_item

router = APIRouter(
    prefix="/companies",
    tags=["Company Management"],
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_companies(
    db: db_dependency,

):
    try:

        result = await db.execute(
            select(Company)

        )
        companies = result.scalars().all()

        return companies
    except Exception as e:
        print("Error:", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_company(db: db_dependency, company_scheme: CompanyScheme):
    try:
        new_company = Company(**company_scheme.model_dump())
        db.add(new_company)
        await db.commit()
        await db.refresh(new_company)

        return response_item(new_company)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.patch("/update/{company_id}", status_code=status.HTTP_200_OK)
async def update_company(
    db: db_dependency, company_id: int, company_scheme: CompanyScheme
):
    try:
        result = await db.execute(
            select(Company).filter(
                Company.id == company_id, Company.is_deleted == False
            )
        )
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
            )

        company.name = company_scheme.name
        await db.commit()
        await db.refresh(company)

        return response_item(item=company)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}"
        )


@router.delete("/delete/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(db: db_dependency, company_id: int):
    try:
        result = await db.execute(
            select(Company).filter(
                Company.id == company_id, Company.is_deleted == False
            )
        )
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
            )

        company.soft_delete()
        await db.commit()

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}"
        )
