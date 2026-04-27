from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from apps import Computer
from apps.base.serializer_fields import SerializerExcludeFields
from apps.computer.routes.serializers.processor_serializer import ProcessorSerializer
from apps.computer.routes.serializers.ram_serializer import RamSerializer
from apps.computer.routes.serializers.storage_serializer import StorageSerializer


class ComputerSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Computer
        load_instance = True
        fields = ('id', 'name', 'rams', 'storages', 'processors') + SerializerExcludeFields.date_fields

    rams = Nested(RamSerializer, many=True)
    storages = Nested(StorageSerializer, many=True)
    processors = Nested(ProcessorSerializer, many=True)
