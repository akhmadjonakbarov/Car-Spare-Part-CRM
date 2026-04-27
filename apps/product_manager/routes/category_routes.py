from fastapi import APIRouter, HTTPException, status
from fastapi import Query
from sqlalchemy import func

from sqlalchemy.exc import SQLAlchemyError

from apps.product_manager.models import Category, Item
from apps.product_manager.schemes import CategoryScheme
from di.db import db_dependency
from utils.response_type import response_item
from .serializers.common_serializers import CategorySerializer

router = APIRouter(
    prefix="/category",
    tags=["Category Management"],
)
from typing import TypeVar
from sqlalchemy import select

T = TypeVar("T")  # Generic model type

from sqlalchemy.orm import selectinload


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_categories(
        db: db_dependency,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
):
    try:
        # total count
        total_result = await db.execute(select(func.count()).select_from(Category))
        total = total_result.scalar_one()

        # calculate offset
        offset = (page - 1) * page_size

        # fetch paginated results with eager loading
        result = await db.execute(
            select(Category)
            .options(
                selectinload(Category.items).selectinload(Item.document_items)
            )
            .filter_by(is_deleted=False)
            .offset(offset)
            .limit(page_size)
        )
        categories = result.scalars().unique().all()

        # serialize safely (no async call inside)
        serializer = CategorySerializer(many=True)
        serialized_items = serializer.dump(categories)

        return {
            "data": {
                "items": serialized_items,
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
async def add_category(db: db_dependency, category_scheme: CategoryScheme):
    """
    Add a new category.
    """
    try:
        new_category = Category(**category_scheme.model_dump())
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)

        return response_item(new_category)

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


@router.patch("/update/{category_id}", status_code=status.HTTP_200_OK)
async def update_category(db: db_dependency, category_id: int, category_scheme: CategoryScheme):
    """
    Update category by ID.
    """
    try:
        result = await db.execute(select(Category).filter_by(id=category_id))
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        category.name = category_scheme.name
        await db.commit()
        await db.refresh(category)

        return response_item(item=category)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/delete/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(db: db_dependency, category_id: int):
    """
    Soft delete a category by ID.
    """
    try:
        result = await db.execute(select(Category).filter_by(id=category_id))
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        category.soft_delete()
        await db.commit()


    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )
