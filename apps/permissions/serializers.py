from marshmallow import fields
from apps.action.serializers import ActionSerializer
from apps.base.schemas import BaseSchema


class PermissionSerializer(BaseSchema):
    name = fields.Str()
    action = fields.Nested(ActionSerializer)
