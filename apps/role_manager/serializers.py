from marshmallow.fields import Nested, Str, Decimal
from apps.base.schemas import BaseSchema


class SalaryTypeSerializer(BaseSchema):
    type_of_salary = Str()


class EmployeeSerializer(BaseSchema):
    base_salary = Decimal()
    salary_type = Nested(SalaryTypeSerializer)
