from typing import Dict

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, delete, insert
from sqlalchemy.orm import selectinload

from apps.product_manager.models import Item, Type, TypeItem
from apps.product_manager.schemas.product import ProductRead
from apps.product_manager.schemes import ItemCreateScheme, ItemUpdateScheme
from di.db import db_dependency
from di.user import user_dependency
from utils.pagination import pagination, PostPagination

router = APIRouter(prefix="/items", tags=["Item Management"])

from sqlalchemy import func


@router.get("/", response_model=PostPagination[Dict])  # Using your generic wrapper
async def get_items(
        db: db_dependency,
        pagination_param: dict = Depends(pagination)
):
    try:
        # 1. Base Query with Eager Loading
        base_query = (
            select(Item)
            .where(Item.is_deleted == False)
            .options(
                selectinload(Item.category),
                selectinload(Item.unit),
                selectinload(Item.company),
                selectinload(Item.types)
            )
            .order_by(Item.created_at.desc())
        )

        # 2. Get Total Count (Crucial for frontend)
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        pages = int(total / pagination_param['limit']) if total > pagination_param['limit'] else 1

        # 3. Apply Pagination Math
        # Use the 'skip' and 'limit' keys from your pagination dependency
        paginated_query = (
            base_query
            .offset(pagination_param['skip'])
            .limit(pagination_param['limit'])
        )

        result = await db.execute(paginated_query)
        items = result.scalars().all()
        flattened_list = []
        for item in items:
            # 1. Create the base data once per item
            base_product = {
                "id": item.id,
                "barcode": item.barcode,
                "sale_price": item.sale_price,
                "income_price": item.income_price,
                "currency_type": item.currency_type,
                "unit": item.unit.value if item.unit else None,  # Safety check for None
                "category": item.category.name if item.category else None,
                "name": item.name,
            }

            if item.types:
                for tp in item.types:
                    row = base_product.copy()
                    row["type"] = tp.name
                    flattened_list.append(row)
            else:

                row = base_product.copy()
                row["type"] = None
                flattened_list.append(row)

        # 4. Return in your PostPagination format
        return {
            "total": total,
            "pages": pages,
            "page": pagination_param['page'],
            "size": pagination_param['limit'],
            "items": flattened_list
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch items: {str(e)}")


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_item(db: db_dependency, user: user_dependency, product_create: ItemCreateScheme):
    try:
        query = (
            select(Item).where(Item.barcode == product_create.barcode)
        )
        res = await db.execute(query)
        product = res.scalar_one_or_none()
        if product:
            raise HTTPException(status_code=400, detail="Product already exists with this barcode")

        product = Item(
            category_id=product_create.category_id,
            unit_id=product_create.unit_id,
            name=product_create.name,
            barcode=product_create.barcode,
            sale_price=product_create.sale_price,
            income_price=product_create.income_price,
            currency_type=product_create.currency_type,
            user_id=user.get("id")
        )
        db.add(product)
        await db.flush()
        if product_create.type_ids:
            types_select_query = (
                select(Type).where(Type.id.in_(product_create.type_ids))
            )
            type_res = await db.execute(types_select_query)
            res = type_res.scalars().all()
            for i in res:
                type_item = TypeItem(
                    type_id=i.id,
                    item_id=product.id
                )
                db.add(type_item)

        await db.commit()

        return {
            "product_id": product.id,
        }

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.patch("/update/{item_id}", response_model=ProductRead)
async def update_item(db: db_dependency, user: user_dependency, item_id: int, item_body: ItemUpdateScheme):
    try:
        res = await db.execute(select(Item).where(Item.id == item_id))
        item: Item = res.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        item.category_id = item_body.category_id
        item.unit_id = item_body.unit_id
        item.name = item_body.name
        item.barcode = item_body.barcode
        item.currency_type = item_body.currency_type
        item.sale_price = item_body.sale_price
        item.income_price = item_body.income_price

        res = await db.execute(select(Type).where(Type.id.in_(item_body.type_ids)))
        types = res.scalars().all()

        # delete old relations
        await db.execute(
            delete(TypeItem).where(TypeItem.item_id == item.id)
        )

        # insert new
        for t in types:
            await db.execute(
                insert(TypeItem).values(item_id=item.id, type_id=t.id)
            )

        await db.commit()
        await db.refresh(item)
        final_query = await db.execute(
            select(Item).options(
                selectinload(Item.category),
                selectinload(Item.unit),
                selectinload(Item.company),
                selectinload(Item.types)
            ).where(Item.id == item.id)
        )

        item = final_query.scalar_one()
        return item

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(db: db_dependency, user: user_dependency, item_id: int):
    try:
        async with db.begin():
            res = await db.execute(select(Item).where(Item.id == item_id))
            item = res.scalar_one_or_none()
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")

            # if item_body.type_name:
            #     res = await db.execute(select(Type).where(Type.name == item_body.type_name))
            #     type_ = res.scalar_one_or_none()
            #     if not type_:
            #         raise HTTPException(status_code=404, detail="Type not found")
            #
            #     await db.execute(
            #         delete(type_item_table).where(
            #             type_item_table.c.item_id == item.id,
            #             type_item_table.c.type_id == type_.id
            #         )
            #     )
            #
            #     if len(item.types) == 0:
            #         item.soft_delete()
            # else:
            item.soft_delete()



    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
