from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from apps.computer.models import Processor, Gen


class GenSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Gen
        load_instance = True
        fields = ('id', 'name')


class ProcessorSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Processor
        load_instance = True
        fields = ('id', 'name', 'gens')

    gens = Nested(GenSerializer, many=True)
