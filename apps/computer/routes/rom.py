from fastapi import APIRouter, HTTPException, status, Depends

from apps import Rom
from apps.computer.routes.schemes import StorageCreateScheme, StorageUpdateScheme
from di.db import db_dependency
from utils.response_type import response_list, response_item

router = APIRouter(
    prefix="/rom",
    tags=["Storage Management"],
)


# Get all storages
@router.get('/all', status_code=status.HTTP_200_OK)
async def get_storages(db: db_dependency):
    try:
        storages = db.query(Rom).all()
        return response_list(lst=storages)
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


# Add new storage
@router.post('/add', status_code=status.HTTP_201_CREATED)
async def add_storage(db: db_dependency, storage: StorageCreateScheme):
    try:
        with db.begin():
            existing_storage = db.query(Rom).filter_by(
                size=storage.size, disk=storage.disk).first()
            if existing_storage:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Storage with this name already exists."
                )
            new_storage = Rom(
                size=storage.size,
                disk=storage.disk
            )
            db.add(new_storage)
            db.flush()

        db.refresh(new_storage)
        return response_item(item=new_storage)
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


# Update existing storage by ID
@router.patch('/update/{storage_id}', status_code=status.HTTP_200_OK)
async def update_storage(storage_id: int, storage: StorageUpdateScheme, db: db_dependency):
    try:
        existing_storage: Rom = db.query(
            Rom).filter(Rom.id == storage_id).first()
        if not existing_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage not found"
            )

        existing_storage.size = storage.size
        existing_storage.disk = storage.disk

        db.commit()
        db.refresh(existing_storage)

        return response_item(item=existing_storage)
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )


# Delete storage by ID
@router.delete('/delete/{storage_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_storage(storage_id: int, db: db_dependency):
    try:
        storage_to_delete: Rom = db.query(
            Rom).filter(Rom.id == storage_id).first()
        if not storage_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage not found"
            )

        storage_to_delete.soft_delete()
        db.commit()
        return {"detail": "Storage deleted successfully"}
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
        )
