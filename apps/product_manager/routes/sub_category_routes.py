from fastapi import APIRouter, HTTPException, status
from fastapi import Query
from sqlalchemy import func

from sqlalchemy.exc import SQLAlchemyError

from apps.product_manager.models import SubCategory, Category
from apps.product_manager.schemes import SubCategoryScheme
from di.db import db_dependency
from utils.response_type import response_item

router = APIRouter(
    prefix="/sub-category",
    tags=["Sub Category Management"],
)
from typing import TypeVar
from sqlalchemy import select

T = TypeVar("T")  # Generic model type

from sqlalchemy.orm import selectinload


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_sub_categories(
        db: db_dependency,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
):
    try:
        total_result = await db.execute(select(func.count()).select_from(SubCategory))
        total = total_result.scalar_one()

        offset = (page - 1) * page_size

        result = await db.execute(
            select(SubCategory)
            .options(selectinload(SubCategory.category))
            .filter_by(is_deleted=False)
            .offset(offset)
            .limit(page_size)
        )
        sub_categories = result.scalars().unique().all()

        serialized = [
            {
                "id": sc.id,
                "name": sc.name,
                "category_id": sc.category_id,
                "category_name": sc.category.name if sc.category else None,
                "created_at": sc.created_at,
                "updated_at": sc.updated_at,
            }
            for sc in sub_categories
        ]

        return {
            "data": {
                "items": serialized,
                "pagination": {
                    "total": total,
                    "page": page,
                    "size": page_size,
                    "pages": (total + page_size - 1) // page_size,
                },
            }
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_sub_category(db: db_dependency, sub_category_scheme: SubCategoryScheme):
    try:
        category = await db.execute(select(Category).filter_by(id=sub_category_scheme.category_id))
        if not category.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Category not found")

        new_sub_category = SubCategory(**sub_category_scheme.model_dump())
        db.add(new_sub_category)
        await db.commit()
        await db.refresh(new_sub_category)

        return response_item(new_sub_category)

    except HTTPException:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.patch("/update/{sub_category_id}", status_code=status.HTTP_200_OK)
async def update_sub_category(db: db_dependency, sub_category_id: int, sub_category_scheme: SubCategoryScheme):
    try:
        result = await db.execute(select(SubCategory).filter_by(id=sub_category_id))
        sub_category = result.scalar_one_or_none()

        if not sub_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sub category not found"
            )

        sub_category.name = sub_category_scheme.name
        sub_category.category_id = sub_category_scheme.category_id
        await db.commit()
        await db.refresh(sub_category)

        return response_item(item=sub_category)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/delete/{sub_category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sub_category(db: db_dependency, sub_category_id: int):
    try:
        result = await db.execute(select(SubCategory).filter_by(id=sub_category_id))
        sub_category = result.scalar_one_or_none()

        if not sub_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sub category not found"
            )

        sub_category.soft_delete()
        await db.commit()

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )
