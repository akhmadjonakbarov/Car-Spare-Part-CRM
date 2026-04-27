# routers/type_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi_pagination import Params
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from marshmallow import Schema, fields
from pydantic import BaseModel, constr

from apps.product_manager.models import Type
from di.db import db_dependency
from di.user import user_dependency
from utils.get_pagination import PaginatedResponse
from utils.response_type import res_message


# ------------------
# Serializers / Schemas
# ------------------

class TypeSerializer(Schema):
    id = fields.Int()
    name = fields.Str()


class TypeCreateScheme(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)


class TypeUpdateScheme(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None


# ------------------
# Router
# ------------------

router = APIRouter(
    prefix="/types",
    tags=["Type Management"],
)


def serialize_type(obj: Type, include_count: bool = True):
    data = {"id": obj.id, "name": obj.name}
    if include_count:
        data["items_count"] = getattr(obj, "items_count", 0)
    return TypeSerializer().dump(data)


@router.get("/all")
async def get_types(
        db: db_dependency,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=100, description="Items per page"),
        q: Optional[str] = Query(None, description="Search by name"),
):
    total_result = await  db.execute(select(func.count()).select_from(Type))
    total = total_result.scalar_one()

    # calculate offset from page and page_size
    offset = (page - 1) * page_size

    # fetch paginated results
    result = await db.execute(
        select(Type).offset(offset).limit(page_size)
    )
    tasks = result.scalars().all()

    serializer = TypeSerializer(many=True)

    return {
        "data": {
            "pagination": {
                "total": total,
                "page": page,
                "size": page_size,
                "pages": (total + page_size - 1) // page_size,  # total pages
            },
            "list": serializer.dump(tasks),
        }
    }


# ==========================
# GET TYPE BY ID
# ==========================
@router.get("/{type_id}")
async def get_type_by_id(type_id: int, db: db_dependency):
    result = await db.execute(select(Type).filter_by(id=type_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Type not found")
    return serialize_type(t)


# ==========================
# CREATE TYPE
# ==========================
@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_type(
        body: TypeCreateScheme,
        db: db_dependency,
        user: user_dependency,
):
    try:
        name = body.name.strip()

        existing = await db.execute(select(Type).where(func.lower(Type.name) == name.lower()))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Type with this name already exists")

        t = Type(name=name)
        db.add(t)
        await db.commit()
        await db.refresh(t)
        return serialize_type(t)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Type with this name already exists")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ==========================
# UPDATE TYPE
# ==========================
@router.patch("/update/{type_id}")
async def update_type(
        type_id: int,
        body: TypeUpdateScheme,
        db: db_dependency,
        user: user_dependency,
):
    try:
        result = await db.execute(select(Type).filter_by(id=type_id))
        t = result.scalar_one_or_none()
        if not t:
            raise HTTPException(status_code=404, detail="Type not found")

        payload = body.model_dump(exclude_unset=True)
        if "name" in payload and payload["name"]:
            new_name = payload["name"].strip()

            existing = await db.execute(
                select(Type)
                .where(func.lower(Type.name) == new_name.lower(), Type.id != type_id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Type with this name already exists")

            t.name = new_name

        await db.commit()
        await db.refresh(t)
        return serialize_type(t)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Type with this name already exists")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ==========================
# DELETE TYPE
# ==========================
@router.delete("/delete/{type_id}", status_code=status.HTTP_200_OK)
async def delete_type(
        type_id: int,
        db: db_dependency,
        user: user_dependency,
):
    try:
        result = await db.execute(select(Type).filter_by(id=type_id))
        t = result.scalar_one_or_none()
        if not t:
            raise HTTPException(status_code=404, detail="Type not found")

        await db.delete(t)
        await db.commit()
        return res_message("Type was deleted successfully")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ==========================
# SIMPLE OPTIONS (no pagination)
# ==========================
@router.get("/options", response_model=List[dict])
async def type_options(db: db_dependency, q: Optional[str] = None):
    stmt = select(Type)
    if q:
        stmt = stmt.filter(Type.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Type.name.asc())

    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [{"id": r.id, "name": r.name} for r in rows]
