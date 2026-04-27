from sqladmin import ModelView
from .models import Role, UsersRoles, SalaryType, Employee


class RoleAdmin(ModelView, model=Role):
    column_list = [Role.id, Role.name, Role.user_id]
    column_searchable_list = [Role.name]
    name = "Role"
    icon = "fa-solid fa-user-shield"


class SalaryTypeAdmin(ModelView, model=SalaryType):
    column_list = [SalaryType.id, SalaryType.type_of_salary]
    name = "Salary Type"
    icon = "fa-solid fa-coins"


class EmployeeAdmin(ModelView, model=Employee):
    column_list = [
        Employee.id,
        Employee.user_id,
        Employee.base_salary,
        Employee.role_id,
    ]
    name = "Employee"
    icon = "fa-solid fa-user-tie"
