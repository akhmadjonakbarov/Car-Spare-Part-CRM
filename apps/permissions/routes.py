from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from apps.action.models import Action
from apps.permissions.models import Permission
from apps.role_manager.models import Role
from di.db import db_dependency
from di.user import user_dependency

from .schemas import PermissionCreate

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions Management"]
)


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_permissions(db: db_dependency):
    """
    Retrieve all permissions.
    """
    try:
        result = await db.execute(select(Permission))
        permissions = result.scalars().all()
        return permissions
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_permission(permission: PermissionCreate, db: db_dependency, user: user_dependency):
    """
    Add a new permission.
    """
    try:
        # Check if role exists
        role_result = await db.execute(select(Role).filter_by(id=permission.role_id))
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found."
            )

        # Check if action exists
        action_result = await db.execute(select(Action).filter_by(id=permission.action_id))
        action = action_result.scalar_one_or_none()
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action not found."
            )

        # Check if permission already exists
        existing_result = await db.execute(
            select(Permission).filter_by(
                role_id=permission.role_id,
                action_id=permission.action_id
            )
        )
        existing_permission = existing_result.scalar_one_or_none()
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists."
            )

        # Create and save new permission
        new_permission = Permission(
            role_id=permission.role_id,
            action_id=permission.action_id
        )

        db.add(new_permission)
        await db.commit()
        await db.refresh(new_permission)

        return new_permission

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )


@router.delete("/delete/{permission_id}", status_code=status.HTTP_200_OK)
async def delete_permission(permission_id: int, db: db_dependency, user: user_dependency):
    """
    Delete a permission by ID.
    """
    try:
        result = await db.execute(select(Permission).filter_by(id=permission_id))
        permission = result.scalar_one_or_none()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found."
            )

        await db.delete(permission)
        await db.commit()

        return {"message": "Permission deleted successfully."}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )
