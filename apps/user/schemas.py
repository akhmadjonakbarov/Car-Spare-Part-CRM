from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from apps.role_manager.schemas import RoleRead


class CreateUserRequest(BaseModel):
    first_name: str = Field(min_length=4)
    last_name: str = Field(min_length=4)
    password: str = Field(min_length=6)
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "akhmad@gmail.com",
                "first_name": "Akhmad",
                "last_name": "akbarov",
                "password": "admin123"
            }
        }


class EmployeeRequest(BaseModel):
    role: str = Field()
    base_salary: float = Field(default=0.0)
    salary_type: str = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "salary_type": "Monthly",
                "role": "Admin",
                "base_salary": 5000.0
            }
        }


class UserRead(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    roles: List[RoleRead]

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "id": 1,
    #             "email": "john.doe@example.com",
    #             "first_name": "John",
    #             "last_name": "Doe",
    #
    #         }
    #     }


class UserResponse(BaseModel):
    access_token: str
    user: UserRead
