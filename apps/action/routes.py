from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from di.db import db_dependency
from di.user import user_dependency
from .models import Action
from .schemas import ActionCreate, ActionUpdate
from .serializers import ActionSerializer

router = APIRouter(
    prefix="/actions",
    tags=["Actions Management"]
)


@router.get("/all")
async def get_actions(db: db_dependency, user: user_dependency = None):
    """
    Retrieve all actions.
    """
    result = await db.execute(select(Action))
    actions = result.scalars().all()

    serializer = ActionSerializer(many=True)
    return serializer.dump(actions)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_action(
        action: ActionCreate,
        db: db_dependency,
        user: user_dependency = None,
):
    """
    Add a new action.
    """
    result = await db.execute(select(Action).filter_by(name=action.name))
    existing_action = result.scalar_one_or_none()

    if existing_action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action with this name already exists."
        )

    new_action = Action(
        name=action.name,
        status=action.status,
        fixed_name=action.fixed_name
    )

    db.add(new_action)
    await db.commit()
    await db.refresh(new_action)
    return new_action


@router.patch("/update/{action_id}", response_model=ActionUpdate)
async def update_action(
        action_id: int,
        action_update: ActionUpdate,
        db: db_dependency,
        user: user_dependency = None,
):
    """
    Update an existing action.
    """
    result = await db.execute(select(Action).filter_by(id=action_id))
    action = result.scalar_one_or_none()

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found."
        )

    action.name = action_update.name or action.name
    action.status = (
        action_update.status if action_update.status is not None else action.status
    )
    action.fixed_name = action_update.fixed_name or action.fixed_name

    await db.commit()
    await db.refresh(action)
    return action


@router.delete("/delete/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(
        action_id: int,
        db: db_dependency,
        user: user_dependency = None,
):
    """
    Delete an action by ID.
    """
    result = await db.execute(select(Action).filter_by(id=action_id))
    action = result.scalar_one_or_none()

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found."
        )

    await db.delete(action)
    await db.commit()

    return {"message": "Action deleted successfully."}
