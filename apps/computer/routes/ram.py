from fastapi.exceptions import HTTPException
from fastapi import APIRouter
from starlette import status

from apps import Ram
from apps.computer.routes.schemes import RamAddScheme, RamUpdateScheme
from di.db import db_dependency

from utils.response_type import response_list, response_item
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/ram",
    tags=["Ram Management"]
)


# Endpoint to get all RAMs
@router.get('/all', status_code=status.HTTP_200_OK)
async def get_rams(db: db_dependency):
    try:
        rams = db.query(Ram).all()
        return response_list(lst=rams)
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post('/add', status_code=status.HTTP_201_CREATED)
async def add_ram(db: db_dependency, ram: RamAddScheme):
    try:
        with db.begin():
            # Check if RAM with the same name already exists
            existing_ram = db.query(Ram).filter_by(size=ram.size).first()  # Assuming 'name' is unique
            if existing_ram:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ram with this name already exists."
                )
            # Create a new RAM object
            new_ram = Ram(
                size=ram.size
            )
            db.add(new_ram)
            db.flush()

        db.refresh(new_ram)
        return response_item(item=new_ram)
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


# Endpoint to update an existing RAM by its ID
@router.patch('/update/{ram_id}', status_code=status.HTTP_200_OK)
async def update_ram(ram_id: int, ram: RamUpdateScheme, db: db_dependency):
    try:
        existing_ram = db.query(Ram).filter(Ram.id == ram_id).first()
        if not existing_ram:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ram not found"
            )

        existing_ram.size = ram.size

        db.commit()
        db.refresh(existing_ram)

        return response_item(item=existing_ram)
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


# Endpoint to delete a RAM by its ID
@router.delete('/delete/{ram_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_ram(ram_id: int, db: db_dependency):
    try:
        ram_to_delete: Ram = db.query(Ram).filter(Ram.id == ram_id).first()
        if not ram_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ram not found"
            )

        ram_to_delete.soft_delete()
        db.commit()
        return {"detail": "Ram deleted successfully"}
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )
