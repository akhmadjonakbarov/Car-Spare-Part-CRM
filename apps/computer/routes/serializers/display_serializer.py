from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from apps.base.serializer_fields import SerializerExcludeFields
from apps.computer.models import Display, DSize, Resolution, RefreshRate


class ResolutionSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Resolution
        load_instance = True
        fields = ('value',) + SerializerExcludeFields.main_fields


class RefreshRateSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = RefreshRate
        load_instance = True
        fields = ('value',) + SerializerExcludeFields.main_fields


class DisplaySizeSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = DSize
        load_instance = True
        fields = ('value',) + SerializerExcludeFields.main_fields


class DisplaySerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = Display
        load_instance = True
        fields = ('name', 'display_sizes', 'resolutions', 'refresh_rates')

    display_sizes = Nested(DisplaySizeSerializer, many=True)
    resolutions = Nested(ResolutionSerializer, many=True)
    refresh_rates = Nested(RefreshRateSerializer, many=True)
