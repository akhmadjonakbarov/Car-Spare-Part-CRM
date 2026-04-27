
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from apps import Ram
from apps.base.serializer_fields import SerializerExcludeFields


class RamSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Ram
        load_instance = True
        fields = ('size',) + SerializerExcludeFields.date_fields
