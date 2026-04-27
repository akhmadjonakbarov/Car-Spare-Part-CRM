# from fastapi import APIRouter, HTTPException, status
# from sqlalchemy.orm import Session
#
# from apps.computer.models import Gen
# from apps.computer.routes.schemes import *
#
# from di.db import db_dependency
# router = APIRouter(
#     prefix="/gens",
#     tags=["Gen Management"],
# )
#
#
# @router.post('/add', status_code=status.HTTP_201_CREATED)
# async def add_gen(db: db_dependency, gen: GenCreateScheme):
#     try:
#         # Check if the gen with the same name already exists for the processor
#         existing_gen = db.query(Gen).filter_by(name=gen.name, processor_id=gen.processor_id).first()
#         if existing_gen:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Gen with this name already exists for this processor."
#             )
#
#         # Create a new gen
#         new_gen = Gen(name=gen.name, processor_id=gen.processor_id)
#         db.add(new_gen)
#         db.commit()
#         db.refresh(new_gen)
#
#         return GenResponseScheme.from_orm(new_gen)
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
#
#
# @router.get('/all', response_model=GenListResponseScheme, status_code=status.HTTP_200_OK)
# async def get_gens(db: db_dependency):
#     try:
#         gens = db.query(Gen).all()
#         return {"items": [GenResponseScheme.from_orm(g) for g in gens]}
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
#
#
# @router.patch('/update/{gen_id}', response_model=GenResponseScheme, status_code=status.HTTP_200_OK)
# async def update_gen(gen_id: int, gen: GenUpdateScheme, db: db_dependency):
#     try:
#         existing_gen = db.query(Gen).filter(Gen.id == gen_id).first()
#         if not existing_gen:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Gen not found"
#             )
#
#         # Update the gen's name and processor_id
#         existing_gen.name = gen.name
#         existing_gen.processor_id = gen.processor_id
#         db.commit()
#         db.refresh(existing_gen)
#
#         return GenResponseScheme.from_orm(existing_gen)
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
#
#
# @router.delete('/delete/{gen_id}', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_gen(gen_id: int, db: db_dependency):
#     try:
#         gen_to_delete: Gen = db.query(Gen).filter(Gen.id == gen_id).first()
#         if not gen_to_delete:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Gen not found"
#             )
#
#         gen_to_delete.soft_delete()
#         db.commit()
#         return {"detail": "Gen deleted successfully"}
#     except Exception as e:
#         raise HTTPException(
#             detail=str(e), status_code=status.HTTP_400_BAD_REQUEST
#         )
