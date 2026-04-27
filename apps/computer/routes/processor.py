from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from apps import Processor
from di.db import db_dependency
from .schemes import *

router = APIRouter(
    prefix="/processors",
    tags=["Processor Management"],
)
#
#
# @router.post('/add', status_code=status.HTTP_201_CREATED)
# async def add_processor(db: db_dependency, processor: ProcessorCreateScheme):
#     try:
#         # Check if the processor with the same name already exists
#         existing_processor = db.query(Processor).filter_by(name=processor.name).first()
#         if existing_processor:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Processor with this name already exists."
#             )
#
#         # Create a new processor
#         new_processor = Processor(name=processor.name)
#         db.add(new_processor)
#         db.commit()
#         db.refresh(new_processor)
#
#         return ProcessorResponseScheme.from_orm(new_processor)
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
#
#
# @router.get('/all', response_model=ProcessorListResponseScheme, status_code=status.HTTP_200_OK)
# async def get_processors(db: db_dependency):
#     try:
#         processors = db.query(Processor).all()
#         return {"items": [ProcessorResponseScheme.from_orm(p) for p in processors]}
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
#
#
# @router.patch('/update/{processor_id}', response_model=ProcessorResponseScheme, status_code=status.HTTP_200_OK)
# async def update_processor(processor_id: int, processor: ProcessorUpdateScheme, db: db_dependency):
#     try:
#         existing_processor = db.query(Processor).filter(Processor.id == processor_id).first()
#         if not existing_processor:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Processor not found"
#             )
#
#         # Update the processor's name
#         existing_processor.name = processor.name
#         db.commit()
#         db.refresh(existing_processor)
#
#         return ProcessorResponseScheme.from_orm(existing_processor)
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
#
#
# @router.delete('/delete/{processor_id}', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_processor(processor_id: int, db: db_dependency):
#     try:
#         processor_to_delete = db.query(Processor).filter(Processor.id == processor_id).first()
#         if not processor_to_delete:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Processor not found"
#             )
#
#         db.delete(processor_to_delete)
#         db.commit()
#         return {"detail": "Processor deleted successfully"}
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
