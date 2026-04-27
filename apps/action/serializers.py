from marshmallow import fields

from apps.base.schemas import BaseSchema


class ActionSerializer(BaseSchema):
    name = fields.Str()
    status = fields.Boolean()
    fixed_name = fields.Str()
