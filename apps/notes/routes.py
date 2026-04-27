from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from di.db import db_dependency
from .models import Note
from apps.product_manager.models import Item

router = APIRouter(
    prefix="/notes",
    tags=["Notes Management"],
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_notes(db: db_dependency):
    try:
        # Use SQLAlchemy async select with join
        stmt = select(Note).options(
            selectinload(Note.item).options(
                selectinload(Item.category),
                selectinload(Item.unit)
            ),
        ).join(Item, Note.item_id == Item.id)
        result = await db.execute(stmt)
        notes = result.scalars().all()

        modified_note = []
        for note in notes:
            modified_note.append(
                {
                    "id": note.item.id,
                    "name": note.item.name,
                    "category": note.item.category.name,
                    "unit": note.item.unit.value,
                }
            )

        return modified_note

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
