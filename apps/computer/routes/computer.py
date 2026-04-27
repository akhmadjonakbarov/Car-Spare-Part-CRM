from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from apps.computer.models import Computer, RomComputer, RamComputer, ProcessorComputer, ComputerDisplay
from apps.computer.routes.schemes import ComputerCreateScheme
from apps.computer.routes.serializers.computer_serializer import ComputerSerializer

from di.db import db_dependency
from utils.get_pagination import PaginatedResponse
from fastapi_pagination import Params

from utils.response_type import response_item

router = APIRouter(
    prefix="/computer",
    tags=["Computer Management"],
)


@router.get('/all')
async def get_computers(db: db_dependency, params: Params = Depends()):
    try:
        computer_pagination = PaginatedResponse(
            db_session=db, model=Computer, params=params, serializer_class=ComputerSerializer
        )
        return computer_pagination.get_paginated_response()
    except Exception as e:
        raise HTTPException(detail=str(
            e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/add', status_code=status.HTTP_201_CREATED)
async def add_computer(computer: ComputerCreateScheme, db: db_dependency):
    try:
        # Create a new computer
        new_computer = Computer(name=computer.name)
        db.add(new_computer)
        db.flush()  # Get the computer ID before adding relationships

        # Add RAMs
        for ram_id in computer.rams:
            ram_computer = RamComputer(
                ram_id=ram_id, computer_id=new_computer.id)
            db.add(ram_computer)

        # Add Storages
        for storage_id in computer.storages:
            storage_computer = RomComputer(
                storage_id=storage_id, computer_id=new_computer.id)
            db.add(storage_computer)

        # Add Processors
        for processor_id in computer.processors:
            processor_computer = ProcessorComputer(
                processor_id=processor_id, computer_id=new_computer.id)
            db.add(processor_computer)

        # Add Displays
        for display_id in computer.displays:
            display_computer = ComputerDisplay(
                display_id=display_id, computer_id=new_computer.id)
            db.add(display_computer)

        db.commit()
        db.refresh(new_computer)

        # Build the response

        return response_item(item=new_computer)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete('/delete/{computer_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_computer(computer_id: int, db: db_dependency):
    try:
        computer: Computer = db.query(Computer).filter(
            Computer.id == computer_id).first()
        if not computer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Computer not found"
            )

        computer.soft_delete()
        db.commit()
        return {"detail": "Computer deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
