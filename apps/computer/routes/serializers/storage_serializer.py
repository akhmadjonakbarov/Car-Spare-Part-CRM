from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from apps.computer.models import Rom
from apps.base.serializer_fields import SerializerExcludeFields


class StorageSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Rom
        load_instance = True
        fields = ('size', 'disk') + SerializerExcludeFields.main_fields
