from marshmallow import fields
from apps.base.schemas import BaseSchema
from apps.permissions.serializers import PermissionSerializer
from apps.role_manager.serializers import EmployeeSerializer


class RoleSerializerWithPermissions(BaseSchema):
    name = fields.Str()
    employees = fields.Nested(EmployeeSerializer, many=True)
    permissions = fields.Nested(PermissionSerializer, many=True)
