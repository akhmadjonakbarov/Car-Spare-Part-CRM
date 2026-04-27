from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from apps.product_manager.models import Unit
from apps.product_manager.schemes import UnitScheme
from di.db import db_dependency
from utils.response_type import response_list, res_message

router = APIRouter(
    prefix="/unit",
    tags=["Unit Management"],
)


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_units(db: db_dependency):
    """
    Get all active units (filtered by is_deleted=False if soft delete is used).
    """
    try:
        result = await db.execute(select(Unit).where(Unit.is_deleted == False))
        units = result.scalars().all()
        return response_list(lst=units)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_unit(db: db_dependency, unit_body: UnitScheme):
    """
    Add a new unit.
    """
    try:
        # Check for duplicates
        result = await db.execute(select(Unit).where(Unit.value.ilike(unit_body.value)))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Unit already exists")

        unit = Unit(**unit_body.model_dump())
        db.add(unit)
        await db.commit()
        await db.refresh(unit)
        return unit

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Unit already exists")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/update/{unit_id}", status_code=status.HTTP_200_OK)
async def update_unit(db: db_dependency, unit_id: int, unit_scheme: UnitScheme):
    """
    Update an existing unit.
    """
    try:
        result = await db.execute(select(Unit).where(Unit.id == unit_id))
        unit = result.scalar_one_or_none()
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")

        # Check for duplicates
        result = await db.execute(
            select(Unit)
            .where(Unit.id != unit_id)
            .where(Unit.value.ilike(unit_scheme.value))
        )
        exists = result.scalar_one_or_none()
        if exists:
            raise HTTPException(status_code=409, detail="Another unit with this value already exists")

        unit.value = unit_scheme.value
        await db.commit()
        await db.refresh(unit)
        return unit

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{unit_id}", status_code=status.HTTP_200_OK)
async def delete_unit(db: db_dependency, unit_id: int):
    """
    Soft delete a unit if supported, otherwise hard delete.
    """
    try:
        result = await db.execute(select(Unit).where(Unit.id == unit_id))
        unit = result.scalar_one_or_none()
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")

        if hasattr(unit, "soft_delete"):
            unit.soft_delete()
        else:
            await db.delete(unit)

        await db.commit()
        return res_message("Unit deleted successfully")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
