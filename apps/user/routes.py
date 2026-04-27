from typing import Annotated, TypeVar

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status

from apps.role_manager.models import SalaryType, Role, Employee, UsersRoles
from apps.user.models import User
from config.security import verify_password, get_password_hash, create_access_token
from di.db import db_dependency
from .schemas import CreateUserRequest, EmployeeRequest, UserResponse

T = TypeVar("T")
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')


class LoginRequest(BaseModel):
    email: str = Field(min_length=6)
    password: str = Field(min_length=6)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def login(db: db_dependency, login_request: LoginRequest = None):
    try:
        query = (
            select(User).options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.roles).selectinload(
                    Role.employees).selectinload(Employee.salary_type)
            ).where(User.email == login_request.email)
        )
        result = await db.execute(
            query
        )
        user: User = result.scalar_one_or_none()

        if not user or not verify_password(login_request.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(email=user.email, user_id=user.id)

        return {
            "user": user,
            "access_token": access_token
        }
    except HTTPException:
        raise


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register(
        db: db_dependency,
        created_user_body: CreateUserRequest,
        created_employee: EmployeeRequest
):
    try:

        # 1. Create the user
        result = await db.execute(
            select(User).where(User.email == created_user_body.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="User already exists")

        created_user = User(
            email=created_user_body.email,
            first_name=created_user_body.first_name,
            last_name=created_user_body.last_name,
            password=get_password_hash(created_user_body.password)
        )
        db.add(created_user)
        await db.flush()

        salary_type = SalaryType(type_of_salary=created_employee.salary_type)
        db.add(salary_type)
        await db.flush()

        role_query = await db.execute(select(Role).where(Role.name == created_employee.role))
        role = role_query.scalar_one_or_none()

        if role is None:
            role = Role(name=created_employee.role)
            db.add(role)
            await db.flush()

        user_role = UsersRoles(user_id=created_user.id, role_id=role.id)
        db.add(user_role)

        employee = Employee(
            role_id=role.id,
            base_salary=created_employee.base_salary,
            salary_type_id=salary_type.id,
            user_id=created_user.id
        )
        db.add(employee)

        await db.commit()

        # 6. EAGER LOAD THE USER FOR RESPONSE
        # This is the "Magic Fix" for your MissingGreenlet error
        final_query = await db.execute(
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.roles).selectinload(
                    Role.employees).selectinload(Employee.salary_type)

            )
            .where(User.id == created_user.id)
        )

        refreshed_user = final_query.scalar_one()

        access_token = create_access_token(
            email=refreshed_user.email, user_id=refreshed_user.id
        )

        return {
            "user": refreshed_user,
            "access_token": access_token,
        }

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database Error: {str(e)}")


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    # Async query using select
    result = await db.execute(select(User).where(User.email == form_data.username))
    user: User | None = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(user.email, user.id)
    return {"access_token": access_token, "token_type": "bearer"}
