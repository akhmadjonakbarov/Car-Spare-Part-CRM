from marshmallow import fields
from apps.role_manager.role_serializers import RoleSerializerWithPermissions
from apps.base.schemas import BaseSchema


class UserSerializer(BaseSchema):
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    roles = fields.Nested(RoleSerializerWithPermissions, many=True)
