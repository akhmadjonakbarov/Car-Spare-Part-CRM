from typing import List

from pydantic import BaseModel

from apps.base.schemas import BaseModelSchema
from apps.permissions.schemas import PermissionRead


class SalaryTypeRead(BaseModel):
    type_of_salary: str

class EmployeeBase(BaseModel):
    id: int

class EmployeeRead(BaseModelSchema):
    id: int
    salary_type: SalaryTypeRead
    base_salary: float



class RoleRead(BaseModelSchema):
    id: int
    name: str
    permissions: List[PermissionRead]
    employees: List[EmployeeRead]
