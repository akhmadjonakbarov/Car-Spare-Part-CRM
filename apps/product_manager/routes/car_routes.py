from fastapi import APIRouter, HTTPException, status
from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from apps.product_manager.models import Car
from apps.product_manager.schemes import CarScheme
from di.db import db_dependency
from utils.response_type import response_item
from .serializers.common_serializers import CarRead

router = APIRouter(
    prefix="/cars",
    tags=["Car Management"],
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_cars(
        db: db_dependency,
):
    try:
        result = await db.execute(
            select(Car)
            .filter_by(is_deleted=False)
        )
        cars = result.scalars().all()

        return cars

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def add_car(db: db_dependency, car_scheme: CarScheme):
    try:
        new_car = Car(**car_scheme.model_dump())
        db.add(new_car)
        await db.commit()
        await db.refresh(new_car)

        return new_car

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


@router.patch("/update/{car_id}", status_code=status.HTTP_200_OK)
async def update_car(
    db: db_dependency, car_id: int, car_scheme: CarScheme
):
    try:
        result = await db.execute(
            select(Car).filter(
                Car.id == car_id, Car.is_deleted == False
            )
        )
        car = result.scalar_one_or_none()

        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
            )

        car.name = car_scheme.name
        await db.commit()
        await db.refresh(car)

        return response_item(item=car)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}"
        )


@router.delete("/delete/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(db: db_dependency, car_id: int):
    try:
        result = await db.execute(
            select(Car).filter(
                Car.id == car_id, Car.is_deleted == False
            )
        )
        car = result.scalar_one_or_none()

        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
            )

        car.soft_delete()
        await db.commit()

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}"
        )
